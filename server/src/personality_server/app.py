"""FastAPI server for personality-based rephrasing."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from personality_server.graph import run_translation
from personality_server.schemas import TranslateRequest, TranslateResponse

load_dotenv()

app = FastAPI(
    title="Personality Server",
    description="Rephrase user text in the voice of a famous personality.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/translate", response_model=TranslateResponse)
async def translate(body: TranslateRequest) -> TranslateResponse:
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not set. Add it to .env or the environment.",
        )

    result = await run_translation(body.personality, body.words)

    if result.get("error_message"):
        return TranslateResponse(
            success=False,
            error=result["error_message"],
        )

    if result.get("evaluation_passed") and result.get("translated_words"):
        return TranslateResponse(
            success=True,
            translated_words=result["translated_words"],
        )

    return TranslateResponse(
        success=False,
        error="The system was unable to translate the message.",
    )


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "personality_server.app:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("RELOAD", "").lower() in ("1", "true", "yes"),
    )


if __name__ == "__main__":
    main()
