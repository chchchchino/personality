"""LangGraph engine: translate text into a famous personality, with evaluator retries."""

from __future__ import annotations

from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from personality_server.schemas import EvaluationResult

MAX_EVALUATION_FAILURES = 2
UNABLE_TO_TRANSLATE_MESSAGE = (
    "The system was unable to translate the message."
)


class PersonalityState(TypedDict):
    personality: str
    original_words: str
    translated_words: str | None
    evaluator_feedback: str | None
    evaluation_passed: bool
    failure_count: int
    error_message: str | None


def _translator_node(state: PersonalityState) -> dict:
    personality = state["personality"]
    original = state["original_words"]
    feedback = state.get("evaluator_feedback")

    system = f"""You are a creative writer who rephrases text in the distinctive voice of {personality}.
Match their known tone, vocabulary, cadence, and mannerisms while preserving the core meaning of the input.
Return only the rephrased text — no preamble, labels, or explanation."""

    user_parts = [f"Rephrase the following as {personality} would say it:\n\n{original}"]
    if feedback:
        user_parts.append(
            f"\n\nYour previous attempt was rejected. Improve it using this feedback:\n{feedback}"
        )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content="".join(user_parts)),
        ]
    )
    translated = (response.content or "").strip()
    return {"translated_words": translated}


def _evaluator_node(state: PersonalityState) -> dict:
    personality = state["personality"]
    original = state["original_words"]
    translated = state.get("translated_words") or ""

    system = """You evaluate whether a rephrased message convincingly sounds like the requested famous person.
The translation must preserve the original meaning and clearly reflect that person's voice and style.
Be fair but strict: generic paraphrases that could be anyone should fail."""

    user = f"""Personality: {personality}

Original text:
{original}

Candidate translation:
{translated}

Decide if this translation passes. If it fails, give concise feedback the translator can use on the next attempt."""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    result: EvaluationResult = llm.with_structured_output(EvaluationResult).invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
    )

    if result.passed:
        return {
            "evaluation_passed": True,
            "evaluator_feedback": result.feedback,
        }

    failure_count = state.get("failure_count", 0) + 1
    if failure_count > MAX_EVALUATION_FAILURES:
        return {
            "evaluation_passed": False,
            "failure_count": failure_count,
            "evaluator_feedback": result.feedback,
            "error_message": UNABLE_TO_TRANSLATE_MESSAGE,
        }

    return {
        "evaluation_passed": False,
        "failure_count": failure_count,
        "evaluator_feedback": result.feedback,
    }


def _route_after_evaluation(
    state: PersonalityState,
) -> Literal["translator", "__end__"]:
    if state.get("error_message"):
        return "__end__"
    if state.get("evaluation_passed"):
        return "__end__"
    return "translator"


def build_graph():
    """Compile the personality translation graph."""
    builder = StateGraph(PersonalityState)
    builder.add_node("translator", _translator_node)
    builder.add_node("evaluator", _evaluator_node)
    builder.add_edge(START, "translator")
    builder.add_edge("translator", "evaluator")
    builder.add_conditional_edges(
        "evaluator",
        _route_after_evaluation,
        {"translator": "translator", "__end__": END},
    )
    return builder.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def run_translation(personality: str, words: str) -> PersonalityState:
    """Run one super-step: translate, evaluate, and retry up to two times on failure."""
    graph = get_graph()
    initial: PersonalityState = {
        "personality": personality.strip(),
        "original_words": words.strip(),
        "translated_words": None,
        "evaluator_feedback": None,
        "evaluation_passed": False,
        "failure_count": 0,
        "error_message": None,
    }
    return await graph.ainvoke(initial)
