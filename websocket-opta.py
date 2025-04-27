import asyncio
import websockets
import websockets.exceptions
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


OUTLET_KEY = os.getenv("OUTLET")

LOG_FILE = "sddp_messages.json"

all_messages = []

def append_to_json_file(msg: dict):
    """Append one message to the main JSON array log file."""
    global all_messages

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "message": msg
    }
    all_messages.append(entry)

    # Write full list back to the file
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(all_messages, f, indent=2)


async def connect_sddp(fixture_uuid, feeds=["matchEvent"], include_opta_id=True):
    uri = "wss://sddp-soccer.performgroup.io"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to SDDP")

            outlet_object = {
                "OutletKeyService": {
                    "outletKey": OUTLET_KEY
                }
            }
            await websocket.send(json.dumps({"outlet": outlet_object}))
            print("Sent outlet auth")

            async for raw_msg in websocket:
                msg = json.loads(raw_msg)

                # 💾 Save full JSON message to file
                append_to_json_file(msg)

                if msg.get("outlet", {}).get("msg") == "is_authorised":
                    print("Authorized! Subscribing to fixture...")

                    subscription_obj = {
                        "name": "subscribe",
                        "feed": feeds,
                        "fixtureUuid": fixture_uuid,
                        "optaId": include_opta_id
                    }

                    await websocket.send(json.dumps({"content": subscription_obj}))
                    print(f"Subscribed to fixture: {fixture_uuid}")

                elif msg.get("outlet", {}).get("msg") == "not_authorised":
                    print("❌ Not authorized! Check your outlet key or IP whitelisting.")
                    print(msg)
                    break

                elif "content" in msg and "liveData" in msg["content"]:
                    print("Live Update:", json.dumps(msg["content"]["liveData"], indent=2))

                else:
                    print("Received message:", msg)

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"⚠️ WebSocket closed unexpectedly: {e}")
    except Exception as e:
        print(f"❗ Unexpected error: {e}")

if __name__ == "__main__":
    # Example usage
    fixture_uuid = "do5ertwz5kefkxoyelso7xpg4"  # Replace with your fixture UUID
    asyncio.run(connect_sddp(fixture_uuid))
