import pytest

@pytest.mark.asyncio
async def test_caption_flow(client):
    s = await client.post("/api/sessions", json={"title": "Standup"})
    sid = s.json()["id"]
    await client.post(f"/api/sessions/{sid}/lines", json={"text": "Hello team", "is_final": True, "latency_ms": 80})
    lines = (await client.get(f"/api/sessions/{sid}/lines")).json()["lines"]
    assert len(lines) == 1
    stats = (await client.get(f"/api/sessions/{sid}/stats")).json()
    assert stats["count"] == 1
