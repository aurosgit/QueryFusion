from flask import Flask, render_template, request
from openai import OpenAI
import os
import requests
import re
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Break question into search queries using OpenAI
def generate_search_queries(question):
    prompt = f"Break this question into 3 Google-style search queries:\n\n{question}\n\nQueries:"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.6,
        )
        text = response.choices[0].message.content
        return [line.strip("1234567890.:- ").strip() for line in text.split("\n") if line.strip()]
    except Exception as e:
        return [f"Error: {str(e)}"]

# Clean result titles to remove uunecessaary words
def clean_title(title):
    return re.sub(r"\[.*?\]", "", title).strip()

# Perform web search using Serper API
def search_web(query):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": os.getenv("SERPER_API_KEY")}
    data = {"q": query}

    try:
        res = requests.post(url, headers=headers, json=data)
        results = res.json().get("organic", [])
        output = []

        for item in results[:3]:  # Take top 3 results per query
            output.append({
                "title": clean_title(item.get("title", "")),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", "#")
            })

        return output
    except Exception as e:
        return [{"title": "Error fetching results", "snippet": str(e), "link": "#"}]

# Use OpenAI to synthesize a summary with citations
def summarize(question, sources):
    if not sources or len(sources) < 2:
        return " Sorry, we couldn’t find enough reliable information to answer your question."

    # Build numbered source text for citation
    source_text = ""
    for idx, src in enumerate(sources, 1):
        source_text += f"[{idx}] {src['title']} - {src['snippet']} ({src['link']})\n"

    # Prompt LLM to answer using citations
    prompt = (
        f"Based on the numbered sources below, answer the question using clear language. "
        f"Use citation references like [1], [2] where appropriate.\n\n"
        f"Question: {question}\n\nSources:\n{source_text}\n\nAnswer:"
    )

    try:
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f" Could not generate summary: {e}"

# Main route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        question = request.form.get("question", "")
        search_queries = generate_search_queries(question)

        search_data = []       # For UI rendering
        all_sources = []       # Flat list of all results for summarization

        for query in search_queries:
            results = search_web(query)
            search_data.append({"query": query, "results": results})
            all_sources.extend(results)

        # Handle insufficient info gracefully
        summary = summarize(question, all_sources)

        return render_template("index.html", question=question, queries=search_data, summary=summary)

    # On GET, render blank form
    return render_template("index.html", question=None)

# Start Flask app
if __name__ == "__main__":
    app.run(debug=True)
