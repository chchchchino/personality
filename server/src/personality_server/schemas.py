"""Pydantic models for API and structured LLM outputs."""

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Structured output from the evaluator node."""

    passed: bool = Field(description="True if the translation convincingly matches the personality")
    feedback: str = Field(description="Brief feedback on what works or what to improve")


class TranslateRequest(BaseModel):
    personality: str = Field(
        ...,
        min_length=1,
        description="Famous person whose voice and style should be used",
    )
    words: str = Field(
        ...,
        min_length=1,
        description="User text to rephrase in that personality",
    )


class TranslateResponse(BaseModel):
    success: bool
    translated_words: str | None = None
    error: str | None = None
