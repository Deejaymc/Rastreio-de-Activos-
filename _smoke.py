import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


async def main() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/")
        print("ROOT_STATUS", r.status_code)
        print("ROOT_CT", r.headers.get("content-type"))
        print("ROOT_HAS_TITLE", "IoT Asset Tracking" in r.text)
        h = await c.get("/health")
        print("HEALTH", h.status_code, h.text)
        a = await c.get("/api/v1/assets?limit=50")
        print("ASSETS", a.status_code, a.text[:120])


asyncio.run(main())
