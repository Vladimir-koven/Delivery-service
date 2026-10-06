from httpx import AsyncClient

from delivery.config import settings


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "delivery-service"
    assert data["env"] == settings.app.env