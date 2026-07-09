import pytest
from unittest.mock import patch, MagicMock
from app.services.commentary import CommentaryService

def test_commentary_service_init():
    service = CommentaryService()
    assert service.is_real_api is False
    assert service.runs == "-"
    assert service.wickets == "-"
    assert service.overs == "-"


def test_commentary_service_simulator_fallback():
    service = CommentaryService()
    # Force empty credentials
    service.api_key = None
    
    state = service.fetch_live_ball("12345")
    
    # Should fall back to simulation, meaning is_real_api remains False
    assert state["is_real_api"] is False
    assert state["overs"] == "0.1"

@patch("requests.get")
def test_commentary_service_api_success(mock_get):
    # Setup mock response matching Cricbuzz RapidAPI structure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "miniscore": {
            "batTeam": {
                "teamScore": 182,
                "teamWickets": 4
            },
            "overs": "18.3",
            "batsmanStriker": {
                "batName": "Hardik Pandya"
            },
            "batsmanNonStriker": {
                "batName": "Rishabh Pant"
            },
            "bowlerStriker": {
                "bowlName": "Mitchell Starc"
            }
        },
        "commentaryList": [
            {
                "commText": "Mitchell Starc to Hardik Pandya, SIX! Launched over long-off!",
                "event": "SIX"
            }
        ]
    }
    mock_get.return_value = mock_response
    
    service = CommentaryService()
    service.api_key = "dummy_key"
    service.api_host = "dummy_host"
    
    state = service.fetch_live_ball("99999")
    
    assert state["is_real_api"] is True
    assert state["score"] == "182/4"
    assert state["overs"] == "18.3"
    assert state["batsman"] == "Hardik Pandya"
    assert state["non_striker"] == "Rishabh Pant"
    assert state["bowler"] == "Mitchell Starc"
    assert "SIX!" in state["raw_commentary"]

@patch("requests.get")
def test_commentary_service_comwrapper_success(mock_get):
    # Setup mock response matching the comwrapper Cricbuzz RapidAPI structure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "inningsid": 0,
        "comwrapper": [
            {
                "commentary": {
                    "commtxt": "B0$ Afghanistan U19 won by 140 runs",
                    "timestamp": 1640430272726,
                    "overnum": 19.4,
                    "inningsid": 2,
                    "eventtype": "NONE"
                }
            }
        ]
    }
    mock_get.return_value = mock_response
    
    service = CommentaryService()
    service.api_key = "dummy_key"
    service.api_host = "dummy_host"
    
    state = service.fetch_live_ball("77777")
    
    assert state["is_real_api"] is True
    # Verify the formatting tags B0$ are correctly cleaned
    assert "B0$" not in state["raw_commentary"]
    assert "Afghanistan U19 won by 140 runs" in state["raw_commentary"]
    assert state["overs"] == "19.4"

