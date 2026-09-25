from __future__ import annotations

import hashlib
import json
from typing import Any

from learning_runtime.capability.curriculum_intelligence import (
    execute_curriculum_query,
)


QUERY = "What is counting?"

VOLATILE_KEYS = {
    "request_id",
    "timestamp",
    "total_latency_ms",
    "latency_ms",
}


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _canonicalize(child)
            for key, child in sorted(value.items())
            if key not in VOLATILE_KEYS
        }

    if isinstance(value, list):
        return [_canonicalize(item) for item in value]

    return value


def _sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _raw_diff_paths(left: Any, right: Any, path: str = "") -> list[str]:
    differences: list[str] = []

    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            child_path = f"{path}.{key}" if path else key

            if key not in left:
                differences.append(child_path)
            elif key not in right:
                differences.append(child_path)
            else:
                differences.extend(_raw_diff_paths(left[key], right[key], child_path))

        return differences

    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return [path]

        for index, (left_item, right_item) in enumerate(zip(left, right)):
            differences.extend(
                _raw_diff_paths(left_item, right_item, f"{path}[{index}]")
            )

        return differences

    if left != right:
        differences.append(path)

    return differences


def test_curriculum_capability_is_deterministic_for_50_runs():
    results = [
        execute_curriculum_query(
            query=QUERY,
            student_id="T_GOV_DETERMINISM",
            grade=1,
            subject="Mathematics",
        )
        for _ in range(50)
    ]

    assert len(results) == 50

    raw_differences = _raw_diff_paths(results[0], results[1])

    for path in raw_differences:
        leaf = path.rsplit(".", 1)[-1]
        assert (
            leaf in VOLATILE_KEYS
        ), f"Unexpected nondeterministic field: {path}"

    canonical_hashes = {
        _sha256_json(_canonicalize(result))
        for result in results
    }

    evidence_hashes = {
        _sha256_json(
            result["result"]["runtime_evidence"]
        )
        for result in results
    }

    status_pairs = {
        (
            result["result"].get("verification_status"),
            result["result"].get("convergence_validated"),
        )
        for result in results
    }

    assert len(canonical_hashes) == 1
    assert len(evidence_hashes) == 1
    assert status_pairs == {("VERIFIED", True)}

    first_result = results[0]["result"]

    assert first_result["evidence_id"]
    assert first_result["textbook_id"] == "BALBHARTI_MATH_G1_MM"
    assert first_result["edition"] == "2023"
    assert first_result["chapter"] == "Counting from 1 to 10"
    assert first_result["section"] == "Number Recognition (1-5)"
    assert first_result["page_numbers"] == [3]
    assert first_result["source_hash"]
    assert first_result["retrieval_hash"]
    assert first_result["lineage_hash"]
