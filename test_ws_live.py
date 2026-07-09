import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8088/api/match/ball"
    print(f"Connecting to WebSocket: {uri}")
    async with websockets.connect(uri) as websocket:
        # Receive the initial state
        init_msg = await websocket.recv()
        print("\n=== Initial State Received ===")
        print(json.dumps(json.loads(init_msg), indent=2))
        
        # Send simulation request
        payload = {
            "action": "simulate",
            "persona": "Ravi Shastri",
            "matchId": "152427"
        }
        print(f"\nSending simulation payload: {payload}")
        await websocket.send(json.dumps(payload))
        
        # Receive update response
        update_msg = await websocket.recv()
        print("\n=== Update Response Received ===")
        print(json.dumps(json.loads(update_msg), indent=2))

if __name__ == "__main__":
    asyncio.run(test_ws())
