# Personality Client

Angular single-page app for the Personality Translator. Enter any personality name, your text, and call the personality server API.

## Prerequisites

- Node.js 18+
- Personality server running on port 8000 (see `../server/README.md`)

## Setup

```bash
cd personality/client
npm install
```

## Development

Start the API server first (in another terminal):

```bash
cd ../server
uv run personality-server
```

Then start the Angular dev server (proxies `/api` → `http://localhost:8000`):

```bash
npm start
```

Open http://localhost:4200

## Build

```bash
npm run build
```
