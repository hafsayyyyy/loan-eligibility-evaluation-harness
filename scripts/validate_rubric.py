import json
from pathlib import Path

RUBRIC_PATH = Path(__file__).resolve().parent.parent / "evaluation_rubric.json"

def validate_rubric():
    with open(RUBRIC_PATH, "r", encoding="utf-8-sig") as file:
        rubric = json.load(file)

    dimensions = rubric.get("dimensions", [])

    assert len(dimensions) >= 3, "At least 3 dimensions required."

    keys = set()
    total_weight = 0

    for dimension in dimensions:
        key = dimension["key"]

        assert key not in keys, "Duplicate dimension found."
        keys.add(key)

        weight = dimension["weight"]
        assert 0 < weight <= 1, f"Invalid weight: {key}"
        total_weight += weight

        anchors = dimension["score_anchors"]

        for score in range(6):
            assert str(score) in anchors, f"Missing score {score} in {key}"

    assert abs(total_weight - 1.0) < 0.000001, "Weights must equal 1.0"

    scoring = rubric["scoring"]

    assert scoring["maximum_score"] == 100
    assert scoring["pass_threshold"] == 75

    print("SUCCESS: Rubric validation passed!")
    print("Dimensions:", len(dimensions))
    print("Total weight:", total_weight)
    print("Pass threshold:", scoring["pass_threshold"])

if __name__ == "__main__":
    validate_rubric()
