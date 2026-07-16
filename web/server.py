from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# T&T Studio catalog — a standalone static site with a tiny config endpoint so
# the Telegram links (bot / manager / channel) are set in Railway Variables
# rather than baked into the built assets.
BOT_USERNAME = os.getenv("SITE_BOT_USERNAME", "").lstrip("@")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "AITimPromptsLab").lstrip("@")
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "Temurali_aliev").lstrip("@")

HERE = os.path.dirname(__file__)

app = FastAPI(title="T&T Studio")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config.json")
async def config() -> dict:
    return {
        "botUsername": BOT_USERNAME,
        "channelUsername": CHANNEL_USERNAME,
        "managerUsername": MANAGER_USERNAME,
    }


# Static frontend last, so /health and /config.json win over the SPA.
app.mount("/", StaticFiles(directory=os.path.join(HERE, "static"), html=True), name="static")


if __name__ == "__main__":
    # Read $PORT in Python rather than a shell-expanded start command: Railway
    # runs the start command without shell `${PORT:-8080}` expansion.
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
