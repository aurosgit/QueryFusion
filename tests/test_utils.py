# tests/test_utils.py

import re
import pytest
from app import clean_title, get_search_queries, get_summary

class DummyResp:
    """Simulates an OpenAI chat response object."""
    def __init__(self, content):
        self.choices = [type("C", (), {
            "message": type("M", (), {"content": content})
        })]

def test_clean_title_strips_brackets():
    assert clean_title("Hello [Ad]") == "Hello"
    assert clean_title("[X] Y [Z]") == "Y"

def test_get_search_queries_numbered(monkeypatch):
    # Simulate GPT returning a numbered list
    fake = DummyResp("1. foo bar\n2. baz qux\n3. quux corge")
    monkeypatch.setattr("app.openai_client.chat.completions.create", lambda **kw: fake)
    qs = get_search_queries("ignored")
    assert qs == ["foo bar", "baz qux", "quux corge"]

def test_get_search_queries_comma(monkeypatch):
    fake = DummyResp("alpha, beta, gamma")
    monkeypatch.setattr("app.openai_client.chat.completions.create", lambda **kw: fake)
    qs = get_search_queries("ignored")
    assert qs == ["alpha", "beta", "gamma"]

def test_get_summary_injects_anchors(monkeypatch):
    sources = [
        {"title":"T1","snippet":"S1","link":"L1"},
        {"title":"T2","snippet":"S2","link":"L2"},
    ]
    fake = DummyResp("Answer part [1] then [2].")
    monkeypatch.setattr("app.openai_client.chat.completions.create", lambda **kw: fake)
    html = get_summary("Q", sources)
    assert re.search(r"<a href='#src1'>\[1\]</a>", html)
    assert re.search(r"<a href='#src2'>\[2\]</a>", html)
