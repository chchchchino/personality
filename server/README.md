# Personality Server

Rephrase user text in the voice of a famous personality. A LangGraph pipeline translates the message, an evaluator checks quality, and failed evaluations trigger up to two retries before returning an error.

## Setup

```bash
cd personality/server
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uv sync
```

## Run the API

```bash
uv run personality-server
# or
uv run uvicorn personality_server.app:app --reload --host 0.0.0.0 --port 8000
```

## API

**POST** `/translate`

```json
{
  "personality": "Winston Churchill",
  "words": "We need to finish the project by Friday."
}
```

Success:

```json
{
  "success": true,
  "translated_words": "...",
  "error": null
}
```

Failure (after more than two failed evaluations):

```json
{
  "success": false,
  "translated_words": null,
  "error": "The system was unable to translate the message."
}
```

Example:

```bash
curl -s -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"personality": "Shakespeare", "words": "The meeting is at 3pm."}'
```
