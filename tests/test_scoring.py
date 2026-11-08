"""Unit tests for the scoring engine."""

import json

import pytest

from scoring import score_response


@pytest.fixture
def rubric() -> dict:
    return {
        "scale": {"minimum": 0, "maximum": 5},
        "dimensions": [
            {"key": "correctness", "weight": 0.5},
            {"key": "completeness", "weight": 0.3},
            {"key": "tone", "weight": 0.2},
        ],
        "scoring": {"pass_threshold": 75},
    }


def test_scores_normal_response(rubric: dict) -> None:
    result = score_response(
        {"scores": {"correctness": 5, "completeness": 4, "tone": 3}},
        rubric,
    )

    assert result["scores"] == {"correctness": 5, "completeness": 4, "tone": 3}
    assert result["overall_score"] == 86.0
    assert result["passed"] is True


def test_accepts_json_strings(rubric: dict) -> None:
    response = json.dumps({"correctness": 4, "completeness": 4, "tone": 4})
    result = score_response(response, json.dumps(rubric))

    assert result["overall_score"] == 80.0


def test_missing_dimension_defaults_to_zero(rubric: dict) -> None:
    result = score_response({"scores": {"correctness": 5}}, rubric)

    assert result["scores"] == {"correctness": 5, "completeness": 0, "tone": 0}
    assert result["overall_score"] == 50.0


def test_extra_keys_are_ignored(rubric: dict) -> None:
    result = score_response(
        {"scores": {"correctness": 5, "completeness": 5, "tone": 5, "unexpected": 99}},
        rubric,
    )

    assert result["scores"] == {"correctness": 5, "completeness": 5, "tone": 5}
    assert result["overall_score"] == 100.0


@pytest.mark.parametrize("bad_json", ["{bad", '{"scores":', "not json"])
def test_malformed_response_json_raises_value_error(
    bad_json: str, rubric: dict
) -> None:
    with pytest.raises(ValueError, match="malformed JSON"):
        score_response(bad_json, rubric)


def test_non_object_response_json_raises_value_error(rubric: dict) -> None:
    with pytest.raises(ValueError, match="must be an object"):
        score_response("[]", rubric)


def test_invalid_scores_fall_back_to_zero_and_are_clamped(rubric: dict) -> None:
    result = score_response(
        {"scores": {"correctness": 99, "completeness": "bad", "tone": -4}},
        rubric,
    )

    assert result["scores"] == {"correctness": 5, "completeness": 0, "tone": 0}
    assert result["overall_score"] == 50.0


def test_direct_dimension_keys_are_supported(rubric: dict) -> None:
    result = score_response(
        {"correctness": 4, "completeness": 3, "tone": 5},
        rubric,
    )

    assert result["scores"] == {"correctness": 4, "completeness": 3, "tone": 5}
    assert result["overall_score"] == 78.0


def test_zero_or_invalid_weight_total_is_rejected(rubric: dict) -> None:
    bad_rubric = {**rubric, "dimensions": [
        {"key": "correctness", "weight": 0},
        {"key": "completeness", "weight": 0},
        {"key": "tone", "weight": 0},
    ]}

    with pytest.raises(ValueError, match="positive total"):
        score_response({"scores": {}}, bad_rubric)
