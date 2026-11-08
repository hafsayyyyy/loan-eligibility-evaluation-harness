"""Scoring engine for evaluating LLM responses against a JSON rubric."""

from __future__ import annotations

import json
from typing import Any


def _parse_response(response: str | dict[str, Any]) -> dict[str, Any]:
    """Parse an LLM response into a dictionary, raising ValueError for invalid JSON."""
    if isinstance(response, dict):
        return response
    if not isinstance(response, str):
        raise TypeError("response must be a JSON string or dictionary")

    try:
        parsed = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response contains malformed JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON must be an object")
    return parsed


def score_response(
    response: str | dict[str, Any],
    rubric: str | dict[str, Any],
) -> dict[str, Any]:
    """Return per-dimension scores and the weighted overall score.

    The LLM response should contain a score for each rubric dimension, either
    directly as {"correctness": 4, ...} or under a "scores" object.
    Missing dimensions receive 0. Extra response keys are ignored. Scores are
    clamped to the rubric's minimum/maximum range and converted to integers.

    The returned overall score follows the rubric formula:
    sum((score / 5) * weight) * 100.
    """
    rubric_data = _parse_response(rubric)
    response_data = _parse_response(response)

    dimensions = rubric_data.get("dimensions", [])
    if not isinstance(dimensions, list):
        raise ValueError("rubric dimensions must be a list")

    scoring = rubric_data.get("scoring", {})
    if not isinstance(scoring, dict):
        scoring = {}

    scale = rubric_data.get("scale", {})
    if not isinstance(scale, dict):
        scale = {}

    minimum = _as_number(scale.get("minimum", 0), 0)
    maximum = _as_number(scale.get("maximum", 5), 5)
    if minimum > maximum:
        raise ValueError("rubric minimum cannot exceed maximum")

    response_scores = response_data.get("scores", response_data)
    if not isinstance(response_scores, dict):
        response_scores = {}

    scores: dict[str, int] = {}
    weights: dict[str, float] = {}

    for dimension in dimensions:
        if not isinstance(dimension, dict):
            continue

        key = dimension.get("key")
        if not isinstance(key, str) or not key:
            continue

        raw_score = response_scores.get(key, minimum)
        score = _coerce_score(raw_score, minimum, maximum)
        scores[key] = score
        weights[key] = _as_number(dimension.get("weight", 0), 0)

    weight_total = sum(weights.values())
    if weight_total <= 0:
        raise ValueError("rubric dimension weights must have a positive total")

    # Normalize weights so malformed-but-usable weights still produce a score.
    overall = sum((scores[key] / maximum) * (weights[key] / weight_total) for key in scores)
    overall_score = round(overall * 100, 2)

    result: dict[str, Any] = {
        "scores": scores,
        "overall_score": overall_score,
    }

    threshold = scoring.get("pass_threshold")
    if isinstance(threshold, (int, float)):
        result["passed"] = overall_score >= threshold

    return result


def _as_number(value: Any, default: float) -> float:
    """Return a numeric value or a safe default."""
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _coerce_score(value: Any, minimum: float, maximum: float) -> int:
    """Convert a score to an integer and clamp it to the rubric scale."""
    if isinstance(value, bool):
        numeric = minimum
    elif isinstance(value, (int, float)):
        numeric = float(value)
    elif isinstance(value, str):
        try:
            numeric = float(value.strip())
        except ValueError:
            numeric = minimum
    else:
        numeric = minimum

    numeric = max(minimum, min(maximum, numeric))
    return int(round(numeric))
