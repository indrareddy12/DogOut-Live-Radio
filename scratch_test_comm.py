import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")

headers = {
    "X-RapidAPI-Key": api_key, 
    "X-RapidAPI-Host": api_host 
}

match_id = "152427"

# Test comm vs hcomm
for endpoint in ["comm", "hcomm"]:
    for iid in [1, 2, 3]:
        url = f"https://{api_host}/mcenter/v1/{match_id}/{endpoint}"
        params = {"iid": iid}
        response = requests.get(url, headers=headers, params=params)
        print(f"Endpoint: {endpoint}, Innings: {iid}, Status: {response.status_code}") 
        if response.status_code == 200:
            data = response.json()
            comwrapper = data.get("comwrapper", [])
            non_empty = [item for item in comwrapper if item.get("commentary", {}).get("commtxt")] 
            print(f"  Total items: {len(comwrapper)}, Non-empty: {len(non_empty)}")
            if non_empty:
                print(f"  Sample text: {non_empty[0].get('commentary', {}).get('commtxt')[:100]}")
