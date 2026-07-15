from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

# The site is a SEPARATE Railway service from the bot. It never imports the bot
# code; it only talks to the already-deployed read-only Catalog API over HTTP.
# Talking to the API server-side (this proxy) instead of from the browser is
# deliberate: it removes the CORS problem entirely (the browser only ever calls
# this same origin) and lets a flaky/sleeping upstream degrade gracefully.
CATALOG_API_BASE = os.getenv(
    "CATALOG_API_BASE",
    "https://empathetic-renewal-production-8293.up.railway.app",
).rstrip("/")

BOT_USERNAME = os.getenv("SITE_BOT_USERNAME", "").lstrip("@")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@zap_tut").lstrip("@")
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "Temurali_aliev").lstrip("@")

HERE = os.path.dirname(__file__)

app = FastAPI(title="zap_tut storefront")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config.json")
async def config() -> dict:
    # The frontend reads link targets from here so bot/channel/manager handles
    # are set in Railway Variables, not baked into the built assets.
    return {
        "botUsername": BOT_USERNAME,
        "channelUsername": CHANNEL_USERNAME,
        "managerUsername": MANAGER_USERNAME,
        "catalogConfigured": bool(CATALOG_API_BASE),
    }


@app.api_route("/api/proxy/{path:path}", methods=["GET"])
async def proxy(path: str, request: Request) -> Response:
    """Forward /api/proxy/<upstream-path> to the Catalog API, preserving the
    query string. Generic on purpose: the upstream mixes prefixes (/products vs
    /api/catalog/brands), so the frontend passes the exact upstream path. A down
    or slow upstream returns 502 as JSON — the frontend renders an offline state
    rather than crashing."""
    url = f"{CATALOG_API_BASE}/{path}"
    query = request.url.query
    if query:
        url = f"{url}?{query}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            upstream = await client.get(url)
    except httpx.HTTPError:
        return JSONResponse({"error": "catalog_unreachable"}, status_code=502)

    media_type = upstream.headers.get("content-type", "application/octet-stream")
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=media_type,
    )


# Static frontend last, so /health, /config.json and /api/* win over the SPA.
app.mount("/", StaticFiles(directory=os.path.join(HERE, "static"), html=True), name="static")


if __name__ == "__main__":
    # Read $PORT in Python rather than a shell-expanded start command: Railway
    # runs the start command without shell `${PORT:-8080}` expansion.
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
