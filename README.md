# QueryFusion 🔍🌐
**Your AI-powered research assistant for fast, cited answers using web search + GPT.**

![Screenshot](./screenshots/QueryFusion_hero.png)

---

## 🚀 Overview

**QueryFusion** is a Flask-based research assistant that:
- Accepts a natural language question
- Breaks it into multiple Google-style sub-queries using OpenAI GPT
- Performs real-time web search using the Serper API
- Synthesizes a concise answer using GPT-3.5
- Cites all sources used to generate the final response

---

## ✨ Features

✅ Input any research-style question  
✅ Auto-generate 2–3 focused web queries  
✅ Fetch results from the web (Serper.dev API)  
✅ Summarize with OpenAI GPT-3.5  
✅ Sources are cited clearly with numbered references  
✅ Handles low-information cases gracefully  
✅ Clean Bootstrap UI with expandable result view

---

## 📸 Screenshots

### Input + Search
![Input Screenshot](./screenshots/Screenshot_input.png)

### Query Breakdown + Search Results
![Search Results](./screenshots/Screenshot_queries.png)

### Summary Output with Citations
![Summary](./screenshots/Screenshot_summary.png)

> You can create a `screenshots/` folder and add your 3 uploaded screenshots named accordingly for clean linking.

---

## 🛠️ Tech Stack

- **Frontend:** HTML, Bootstrap 5
- **Backend:** Python, Flask
- **LLM API:** OpenAI GPT-3.5-turbo
- **Search API:** Serper.dev (Google Search alternative)

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/aurosgit/QueryFusion.git
cd QueryFusion
