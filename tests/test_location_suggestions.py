import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_suggest_locations_returns_list(client: AsyncClient):
    resp = await client.get("/hotels/locations/suggest", params={"q": "а"})
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)


@pytest.mark.asyncio
async def test_suggest_locations_requires_query(client: AsyncClient):
    resp = await client.get("/hotels/locations/suggest")
    assert resp.status_code == 422
