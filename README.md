# Personality Translator

Rephrase any text in the voice of a famous person from history or pop culture. This repo has two parts:

| Directory | Stack | Role |
|-----------|--------|------|
| [`server/`](server/) | Python, UV, LangGraph, FastAPI | Translates text with an LLM pipeline (translator + evaluator, up to 3 attempts) |
| [`client/`](client/) | Angular, Bootstrap | Web UI with a personality text field, textarea, and results |

## Prerequisites

Install these before you start:

- **Python 3.11+** and **[uv](https://docs.astral.sh/uv/)** (server)
- **Node.js 18+** and **npm** (client)
- **OpenAI API key** ([platform.openai.com](https://platform.openai.com/api-keys))

## Quick start

Clone the repo, then run the server and client in **two terminals**.

### 1. Server (API on port 8000)

```bash
cd server
cp .env.example .env
```

Add your `OPENAI_API_KEY` to `server/.env`, then:

```bash
uv sync
uv run personality-server
```

Confirm the API is up:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 2. Client (UI on port 4200)

In a second terminal:

```bash
cd client
npm install
npm start
```

Open **http://localhost:4200**, type a personality (any famous person or character), enter text, and click **Translate**.

The dev server proxies `/api/*` to `http://localhost:8000`, so you do not need extra CORS setup for local development.

## Project layout

```
personality/
├── README.md          ← you are here
├── server/            ← FastAPI + LangGraph backend
│   ├── README.md      ← API details, curl examples
│   ├── .env.example
│   └── src/personality_server/
└── client/            ← Angular frontend
    ├── README.md      ← build & dev notes
    └── src/app/
```

## How it works

1. The **client** sends `personality` and `words` to `POST /translate`.
2. The **server** runs a LangGraph flow: a translator node rephrases the text; an evaluator node checks voice and meaning.
3. If evaluation fails, the translator retries (up to two retries). After more than two failed evaluations, the API returns an error message.
4. The client shows the translated text or the error.

Default model: **gpt-4o-mini** (see `server/src/personality_server/graph.py`).

## API (summary)

**POST** `http://localhost:8000/translate`

```json
{
  "personality": "Winston Churchill",
  "words": "We need to finish the project by Friday."
}
```

Success response:

```json
{
  "success": true,
  "translated_words": "...",
  "error": null
}
```

Full request/response examples and curl commands: [`server/README.md`](server/README.md).

## Production build (client only)

```bash
cd client
npm run build
```

Output is in `client/dist/client/`. Point your static host at that folder and configure it to proxy `/api` to your deployed server (or set the API base URL in the Angular service).

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| `OPENAI_API_KEY is not set` | `server/.env` exists and contains a valid key |
| Client shows a network error | Server is running on port 8000 (`uv run personality-server`) |
| Port already in use | Change server port: `PORT=8001 uv run personality-server` (client proxy targets 8000 by default; update `client/proxy.conf.json` if needed) |
| `uv: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

## More documentation

- **Server setup, API, curl examples:** [`server/README.md`](server/README.md)
- **Client dev server, build, proxy:** [`client/README.md`](client/README.md)
