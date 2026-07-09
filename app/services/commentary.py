import os
import re
import random
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# A database of pre-written classic cricket commentary events to sync with the match simulator.
HISTORIC_COMMENTARY = [
    {"event": "Dot Ball", "desc": "Good length delivery outside off, left alone by the batsman."},
    {"event": "Single", "desc": "Tucked away off the hips towards deep square leg for a comfortable single."},
    {"event": "Two Runs", "desc": "Nudged into the gap at mid-wicket, swift running between the wickets to get two."},
    {"event": "Boundary Four", "desc": "Cracked through the covers! What a magnificent shot, racing away to the boundary for four!"},
    {"event": "Sixer", "desc": "He has launched that! High, handsome, and all the way over long-on for a monumental six!"},
    {"event": "Wicket (Bowled)", "desc": "OUT! Clean bowled! He went for the big heave, missed it completely, and the off-stump is knocked out of the ground!"},
    {"event": "Wicket (Caught)", "desc": "OUT! Caught! Tried to clear the boundary but got a leading edge, and it is a simple catch for the fielder at deep mid-wicket."},
    {"event": "No Ball", "desc": "Overstepping by the bowler! Free hit coming up next ball."},
    {"event": "Wide Ball", "desc": "Fired down the leg side, too wide, batsman cannot reach it."},
    {"event": "Single", "desc": "Driven gently down to long-off to rotate the strike."}
]

PLAYERS_BATSMEN = ["Virat Kohli", "Rohit Sharma", "KL Rahul", "Suryakumar Yadav", "Hardik Pandya", "Rishabh Pant"]
PLAYERS_BOWLERS = ["Shaheen Afridi", "Mitchell Starc", "Jasprit Bumrah", "Pat Cummins", "Trent Boult", "Rashid Khan"]

class CommentaryService:
    def __init__(self):
        # Default fallback/simulator state
        self.runs = "-"
        self.wickets = "-"
        self.overs = "-"
        self.batsman = "Waiting..."
        self.non_striker = "Waiting..."
        self.bowler = "Waiting..."
        self.last_event_type = "Waiting..."
        self.last_description = "Match starting..."
        self.is_real_api = False
        self.bat_team_name = "--"
        
        # Playback cache engine to step through static match commentaries
        self.cached_match_id = None
        self.commentary_items = []  # Chronological list of balls
        self.commentary_index = 0
        self.cached_scorecard = {}
        
        # Load API keys
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
        self.match_id = os.getenv("CRICKET_MATCH_ID")
        print(f"DEBUG SERVICE INIT: api_key={self.api_key}, api_host={self.api_host}, match_id={self.match_id}", flush=True)

    def get_state(self) -> Dict[str, Any]:
        return {
            "score": f"{self.runs}/{self.wickets}",
            "overs": f"{self.overs}",
            "batsman": self.batsman,
            "non_striker": self.non_striker,
            "bowler": self.bowler,
            "last_event": self.last_event_type,
            "raw_commentary": f"{self.overs}: {self.last_description}" if self.is_real_api else f"{self.overs}: {self.bowler} to {self.batsman}, {self.last_description}",
            "is_real_api": self.is_real_api,
            "default_match_id": self.match_id,
            "team_name": self.bat_team_name
        }

    def fetch_live_ball(self, match_id: str = None) -> Dict[str, Any]:
        target_match_id = match_id or self.match_id
        print(f"DEBUG fetch_live_ball: target_match_id={target_match_id}, api_key_configured={bool(self.api_key)}, api_host={self.api_host}", flush=True)
        
        if not self.api_key or not target_match_id:
            print("DEBUG fetch_live_ball: Missing API Key or Match ID. Falling back to simulator.", flush=True)
            self.is_real_api = False
            return self.simulate_next_ball()
            
        try:
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": self.api_host
            }
            
            # Reset cache if match ID changes
            if self.cached_match_id != target_match_id:
                print(f"DEBUG fetch_live_ball: Target match ID changed or first load. Fetching from API.", flush=True)
                self.cached_match_id = target_match_id
                self.commentary_items = []
                self.commentary_index = 0
                self.cached_scorecard = {}
                
                # Fetch scorecard details once
                scorecard_url = f"https://{self.api_host}/mcenter/v1/{target_match_id}/hscard"
                print(f"DEBUG fetch_live_ball: Fetching Scorecard API: {scorecard_url}", flush=True)
                sc_response = requests.get(scorecard_url, headers=headers, timeout=5)
                
                active_innings_id = 1
                if sc_response.status_code == 200:
                    self.cached_scorecard = sc_response.json()
                    scorecard_list = self.cached_scorecard.get("scorecard", []) or self.cached_scorecard.get("scoreCard", [])
                    if scorecard_list:
                        # Extract the active innings ID (inningsid)
                        active_innings_id = scorecard_list[-1].get("inningsid", 1)
                    else:
                        innings = self.cached_scorecard.get("innings", [])
                        if innings:
                            active_innings_id = innings[-1].get("inningsid", 1)
                            
                print(f"DEBUG fetch_live_ball: Detected active innings ID={active_innings_id}", flush=True)
                
                # Fetch commentary with sequential innings fallbacks using `/comm` endpoint
                comm_url = f"https://{self.api_host}/mcenter/v1/{target_match_id}/comm"
                
                for iid in range(active_innings_id, 0, -1):
                    params = {"iid": iid}
                    print(f"DEBUG fetch_live_ball: Fetching Commentary API: {comm_url} with params {params}", flush=True)
                    response = requests.get(comm_url, headers=headers, params=params, timeout=5)
                    
                    if response.status_code == 200:
                        comm_data = response.json()
                        
                        # 1. Try comwrapper
                        comwrapper = comm_data.get("comwrapper", [])
                        temp_items = []
                        for item in comwrapper:
                            comm_obj = item.get("commentary", {})
                            if comm_obj and comm_obj.get("commtxt"):
                                temp_items.append({
                                    "commtxt": comm_obj.get("commtxt"),
                                    "overnum": comm_obj.get("overnum"),
                                    "eventtype": comm_obj.get("eventtype")
                                })
                                
                        # 2. Try older format commentaryList
                        if not temp_items:
                            commentary_list = comm_data.get("commentaryList", [])
                            for comm_item in commentary_list:
                                if comm_item.get("commText"):
                                    temp_items.append({
                                        "commtxt": comm_item.get("commText"),
                                        "overnum": comm_item.get("over"),
                                        "eventtype": comm_item.get("event")
                                    })
                        
                        if temp_items:
                            temp_items.reverse()  # Oldest to newest
                            self.commentary_items = temp_items
                            print(f"DEBUG fetch_live_ball: Loaded {len(self.commentary_items)} commentaries from innings {iid}", flush=True)
                            
                            # Also update the scorecard elements to match this specific innings so players and scores align!
                            if self.cached_scorecard:
                                scorecard_list = self.cached_scorecard.get("scorecard", []) or self.cached_scorecard.get("scoreCard", [])
                                matched_innings = None
                                if scorecard_list:
                                    for inn in scorecard_list:
                                        if inn.get("inningsid") == iid:
                                            matched_innings = inn
                                            break
                                if matched_innings:
                                    self.runs = matched_innings.get("score", self.runs)
                                    self.wickets = matched_innings.get("wickets", self.wickets)
                                    self.overs = str(matched_innings.get("overs", self.overs))
                                    self.bat_team_name = matched_innings.get("batteamsname", matched_innings.get("batTeamName", self.bat_team_name))
                                    
                                    bat_card = matched_innings.get("batsman", []) or matched_innings.get("batCard", [])
                                    active_batsmen = []
                                    for batsman_obj in bat_card:
                                        out_desc = batsman_obj.get("outdec", batsman_obj.get("outDesc", ""))
                                        if not out_desc or out_desc.lower() == "batting" or out_desc.lower() == "not out":
                                            active_batsmen.append(batsman_obj.get("name", ""))
                                    if active_batsmen:
                                        self.batsman = active_batsmen[0]
                                        self.non_striker = active_batsmen[1] if len(active_batsmen) > 1 else "Not out"
                                    
                                    bowl_card = matched_innings.get("bowler", []) or matched_innings.get("bowlCard", [])
                                    if bowl_card:
                                        self.bowler = bowl_card[-1].get("name", self.bowler)
                                else:
                                    # Fallback to miniscore / matchScore (older Cricbuzz formats)
                                    miniscore = self.cached_scorecard.get("miniscore", {}) or self.cached_scorecard.get("matchScore", {})
                                    if miniscore:
                                        bat_team = miniscore.get("batTeam", {}) or miniscore.get("batteam", {})
                                        if bat_team:
                                            self.runs = bat_team.get("teamScore", bat_team.get("teamscore", self.runs))
                                            self.wickets = bat_team.get("teamWickets", bat_team.get("teamwickets", self.wickets))
                                        
                                        overs_val = miniscore.get("overs")
                                        if overs_val is not None:
                                            self.overs = str(overs_val)
                                            
                                        batsman_striker = miniscore.get("batsmanStriker", {}) or miniscore.get("batStriker", {})
                                        if batsman_striker:
                                            self.batsman = batsman_striker.get("batName", batsman_striker.get("name", self.batsman))
                                        
                                        batsman_non_striker = miniscore.get("batsmanNonStriker", {}) or miniscore.get("batNonStriker", {})
                                        if batsman_non_striker:
                                            self.non_striker = batsman_non_striker.get("batName", batsman_non_striker.get("name", self.non_striker))
                                        
                                        bowler_striker = miniscore.get("bowlerStriker", {}) or bowler_striker.get("bowlStriker", {})
                                        if bowler_striker:
                                            self.bowler = bowler_striker.get("bowlName", bowler_striker.get("name", self.bowler))
                            break
            
            # Check if we have commentaries in the playback queue
            if not self.commentary_items:
                print("DEBUG fetch_live_ball: No commentaries found in API response. Falling back to simulator.", flush=True)
                self.is_real_api = False
                return self.simulate_next_ball()
                
            # Retrieve the current ball to play from the queue
            comm_obj = self.commentary_items[self.commentary_index]
            print(f"DEBUG fetch_live_ball: Playing ball index {self.commentary_index}/{len(self.commentary_items)}", flush=True)
            
            # Advance index for the next click (loop back if we reach the end)
            self.commentary_index = (self.commentary_index + 1) % len(self.commentary_items)
            
            # Parse ball description and over number
            comm_text = comm_obj.get("commtxt", "")
            clean_text = re.sub(r'[B-Z]\d+\$', '', comm_text).strip()
            self.last_description = clean_text
            
            over_num = comm_obj.get("overnum")
            if over_num is not None:
                self.overs = str(over_num)
                
            # Determine event type
            event_tag = comm_obj.get("eventtype", "NONE") or comm_obj.get("eventtype", "NONE")
            event_tag = str(event_tag).upper()
            if "WICKET" in event_tag or "OUT" in event_tag:
                self.last_event_type = "Wicket (Caught)"
            elif "FOUR" in event_tag or "4" in event_tag:
                self.last_event_type = "Boundary Four"
            elif "SIX" in event_tag or "6" in event_tag:
                self.last_event_type = "Sixer"
            elif "WIDE" in event_tag:
                self.last_event_type = "Wide Ball"
            elif "NO BALL" in event_tag:
                self.last_event_type = "No Ball"
            else:
                text_lower = clean_text.lower()
                if "no run" in text_lower or "dot ball" in text_lower:
                    self.last_event_type = "Dot Ball"
                elif "1 run" in text_lower or "single" in text_lower:
                    self.last_event_type = "Single"
                elif "2 runs" in text_lower:
                    self.last_event_type = "Two Runs"
                else:
                    self.last_event_type = "Dot Ball"
                    
            self.is_real_api = True
            return self.get_state()
            
        except Exception as e:
            print(f"CRICBUZZ API EXCEPTION: {e}", flush=True)
            import traceback
            traceback.print_exc()
            self.is_real_api = False
            return self.simulate_next_ball()

    def simulate_next_ball(self) -> Dict[str, Any]:
        if self.batsman == "Waiting...":
            self.runs = 0
            self.wickets = 0
            self.overs = "0.0"
            self.batsman = PLAYERS_BATSMEN[0]
            self.non_striker = PLAYERS_BATSMEN[1]
            self.bowler = PLAYERS_BOWLERS[0]
            
        self.bat_team_name = "IND"
        try:
            overs_float = float(self.overs)
        except ValueError:
            overs_float = 0.0
            
        current_over = int(overs_float)
        current_ball = int(round((overs_float - current_over) * 10))
        
        current_ball += 1
        if current_ball >= 6:
            current_ball = 0
            current_over += 1
            new_bowlers = [b for b in PLAYERS_BOWLERS if b != self.bowler]
            self.bowler = random.choice(new_bowlers)
            self.batsman, self.non_striker = self.non_striker, self.batsman
            
        self.overs = f"{current_over + (current_ball / 10.0):.1f}"
        
        event = random.choice(HISTORIC_COMMENTARY)
        self.last_event_type = event["event"]
        self.last_description = event["desc"]
        
        if event["event"] == "Single":
            self.runs += 1
            self.batsman, self.non_striker = self.non_striker, self.batsman
        elif event["event"] == "Two Runs":
            self.runs += 2
        elif event["event"] == "Boundary Four":
            self.runs += 4
        elif event["event"] == "Sixer":
            self.runs += 6
        elif event["event"] == "Wicket (Bowled)" or event["event"] == "Wicket (Caught)":
            self.wickets += 1
            if self.wickets < 10:
                used_batsmen = [self.batsman, self.non_striker]
                available_batsmen = [b for b in PLAYERS_BATSMEN if b not in used_batsmen]
                if available_batsmen:
                    self.batsman = available_batsmen[0]
                else:
                    self.batsman = "New Batsman"
            else:
                self.runs = 0
                self.wickets = 0
                self.overs = "0.0"
                self.batsman = PLAYERS_BATSMEN[0]
                self.non_striker = PLAYERS_BATSMEN[1]
                self.bowler = PLAYERS_BOWLERS[0]
                self.last_description = "Innings over! All out. Resetting match..."
                self.last_event_type = "Innings Over"
                
        elif event["event"] == "No Ball" or event["event"] == "Wide Ball":
            self.runs += 1
            current_ball -= 1
            if current_ball < 0:
                current_ball = 5
                current_over -= 1
                if current_over < 0:
                    current_over = 0
                    current_ball = 0
            self.overs = f"{current_over + (current_ball / 10.0):.1f}"

        return self.get_state()
