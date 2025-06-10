import os
import re
import logging
import requests
from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
if not OPENAI_API_KEY or not SERPER_API_KEY:
    raise RuntimeError("Please set both OPENAI_API_KEY and SERPER_API_KEY in your environment.")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Config
RESULTS_PER_QUERY = 3
MAX_SOURCES = 5


def get_search_queries(question: str) -> list[str]:
    """
    Ask the model for 3 concise search queries.
    Splits the model's response into separate queries by numbering or newlines.
    """
    prompt = (
        f"Please list three distinct search queries for the question below. "
        f"Number them 1., 2., 3. and separate by newlines:\n{question}"
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.6,
        )
        text = resp.choices[0].message.content.strip()
        # Split on lines or commas
        parts = re.split(r"\n|,", text)
        queries = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Remove leading numbers and punctuation
            clean = re.sub(r"^\d+[\). -]*", "", part).strip()
            queries.append(clean)
            if len(queries) == 3:
                break
        # Fallback: full text as one query
        return queries if queries else [text]
    except Exception as e:
        logger.error("Failed to get search queries: %s", e, exc_info=True)
        return []


def clean_title(title: str) -> str:
    return re.sub(r"\[.*?\]", "", title).strip()


def search_web(query: str) -> list[dict]:
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY}
    try:
        res = requests.post(url, headers=headers, json={"q": query}, timeout=10)
        res.raise_for_status()
        items = res.json().get('organic', [])[:RESULTS_PER_QUERY]
        results = []
        for item in items:
            title = clean_title(item.get('title', ''))
            snippet = item.get('snippet', '')
            link = item.get('link', '#')
            if title and snippet:
                results.append({'title': title, 'snippet': snippet, 'link': link})
        return results
    except Exception as e:
        logger.error("Search error: %s", e, exc_info=True)
        return []


def get_summary(question: str, sources: list[dict]) -> str:
    if len(sources) < 2:
        return "Sorry, not enough data."
    citation_block = ""
    for i, src in enumerate(sources, 1):
        citation_block += f"[{i}] {src['title']} ({src['link']}) - {src['snippet']}\n"
    prompt = (
        f"Answer the question with citations [1], [2], [3]:\n{question}\nSources:\n{citation_block}\nAnswer:"
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.7,
        )
        summary = resp.choices[0].message.content.strip()
        # Link citations to source list below
        return re.sub(r"\[(\d+)\]", lambda m: f"<a href='#src{m.group(1)}'>[{m.group(1)}]</a>", summary)
    except Exception as e:
        logger.error("Summary error: %s", e, exc_info=True)
        return "Could not summarize."

# Flask setup
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    question = None
    queries = []
    sources = []
    summary = None
    if request.method == 'POST':
        question = request.form['question'].strip()
        if not question:
            error = 'Enter a question.'
        else:
            qs = get_search_queries(question)
            raw = []
            for q in qs:
                hits = search_web(q)
                raw.append({'query': q, 'results': hits})
            all_hits = [h for grp in raw for h in grp['results']]
            seen = set()
            for h in all_hits:
                if h['link'] not in seen:
                    sources.append(h)
                    seen.add(h['link'])
                if len(sources) == MAX_SOURCES:
                    break
            summary = get_summary(question, sources)
            queries = raw
    return render_template('index.html', error=error, question=question,
                           queries=queries, summary=summary, sources=sources)

if __name__ == '__main__':
    app.run(debug=True)