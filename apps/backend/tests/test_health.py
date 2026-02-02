import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client) -> None:
    response = await client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "app_db" in data
    assert "users_db" in data
    assert "redis" in data
