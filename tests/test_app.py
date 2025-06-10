# tests/test_app.py

import pytest
from app import app

@pytest.fixture
def client(monkeypatch):
    # Stub core functions so no real API calls happen:
    monkeypatch.setattr("app.get_search_queries", lambda q: ["q1","q2","q3"])
    monkeypatch.setattr("app.search_web", lambda q: [{"title":"X","snippet":"Y","link":"Z"}])
    # Stub get_summary to return clickable anchor HTML
    monkeypatch.setattr(
        "app.get_summary",
        lambda q, s: "Here is <a href='#src1'>[1]</a>"
    )
    return app.test_client()

def test_home_page_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Ask me anything" in res.data

def test_home_post_shows_summary_and_source(client):
    res = client.post("/", data={"question":"Hello?"})
    assert res.status_code == 200
    # Our stub now includes the HTML anchor
    assert b"Here is <a href='#src1'>[1]</a>" in res.data
    # Stub source link
    assert b"href=\"Z\"" in res.data
