import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(
    filename="match_events.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

ALLOWED_IPS = {"127.0.0.1", "::1"}


@app.get("/")
def read_root():
    return {"message": "Hello World!"}


@app.post("/match/events")
async def receive_match_events(request: Request, event: dict):
    client_host = request.client.host
    logging.info(f"Request received from IP: {client_host}")

    if client_host not in ALLOWED_IPS:
        logging.warning(f"Unauthorized access attempt from IP: {client_host}")
        return JSONResponse(
            status_code=403, content={"detail": "Forbidden: Unauthorized IP"}
        )

    # Process the event here
    logging.info(f"Received match event: {event}")

    return {"status": "success", "event": event}
