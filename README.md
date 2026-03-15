# smart-repo-docs 📄

A tool I built that automatically generates README files and documentation for any GitHub repo or local project folder. You paste a GitHub URL or a local path, it reads the codebase and generates structured Markdown docs using the Gemini API.

## Why I built this

I kept spending way too much time writing READMEs for my own projects. Wanted to see if I could automate it using an LLM. Ended up building a small web app around it with FastAPI and a clean frontend.

## How it works

1. You give it a GitHub URL or a local folder path
2. It clones/reads the repo and builds a full text context of the codebase
3. Sends that context to Gemini with a structured prompt
4. Returns clean Markdown documentation in the browser

## Tech used

- Python 3 + FastAPI — backend API
- Uvicorn — ASGI server
- Google Gemini API (`gemini-2.5-flash`) — doc generation
- HTML + CSS + JavaScript — frontend
- `marked.js` — renders Markdown in the browser
- `highlight.js` — syntax highlighting for code blocks
- `pathspec` — respects `.gitignore` when reading files

## Setup

```bash
git clone https://github.com/Spoorti-I/smart-repo-docs.git
cd smart-repo-docs

python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file in the root folder:
```
GEMINI_API_KEY=your_api_key_here
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

Then run:
```bash
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

## Project structure

```
smart-repo-docs/
├── main.py              # FastAPI app, API routes
├── utils/
│   ├── ai_generator.py  # Gemini API calls and prompt logic
│   └── file_parser.py   # reads codebase, builds context string
├── static/
│   ├── index.html       # frontend UI
│   ├── script.js        # handles API calls and rendering
│   └── styles.css       # dark theme styling
├── requirements.txt
└── .env                 # not committed — add your own
```

## What I learned

- Building REST APIs with FastAPI
- Prompt engineering — getting consistent structured output from Gemini
- Handling file system traversal and .gitignore parsing in Python
- Connecting a vanilla JS frontend to a Python backend

## Known issues / TODO

- local folder path only works if the server is running on the same machine
- very large repos sometimes hit token limits
- want to add support for multiple output formats (not just Markdown)
- UI could use some improvement on mobile

---

Built by [Spoorti Inganalli](https://linkedin.com/in/spoortiinganalli) · KLE Institute of Technology, Hubli
