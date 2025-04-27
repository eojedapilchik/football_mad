from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Define your allowed IP(s)
ALLOWED_IPS = {"127.0.0.1", "::1"}  # localhost IPv4 and IPv6


# You can add your server's public IP here too


@app.get("/")
def read_root():
    return {"message": "Hello World!"}


@app.post("/match/events")
async def receive_match_events(request: Request, event: dict):
    client_host = request.client.host
    print(f"Request received from IP: {client_host}")

    if client_host not in ALLOWED_IPS:
        return JSONResponse(
            status_code=403, content={"detail": "Forbidden: Unauthorized IP"}
        )

    # Process the event here
    print(f"Received match event: {event}, headers: {request.headers}")
    return {"status": "success", "event": event}
