from copy import deepcopy

import pytest

import learning_runtime.canonical_runtime as canonical_runtime
from learning_runtime.capability.curriculum_intelligence import capability_metadata


def valid_fixture():
    payload = canonical_runtime.retrieve_from_masterdb(
        query="What is counting?",
        grade=1,
        subject="Mathematics",
    )
    return deepcopy(payload["best_record"]), deepcopy(payload["best_record"]["evidence"])


def test_capability_metadata_is_complete():
    metadata = capability_metadata()

    assert metadata["capability_id"] == "tantra.curriculum_intelligence"
    assert metadata["version"] == "1.0.0"
    assert metadata["schema"] == "TANTRA_CURRICULUM_INTELLIGENCE_CAPABILITY_V1"
    assert metadata["execution_mode"] == "deterministic"
    assert metadata["evidence_required"] is True
    assert metadata["replay_safe"] is True


def test_load_json_file_rejects_missing_file(tmp_path):
    runtime = canonical_runtime.CanonicalRuntime()

    with pytest.raises(ValueError, match="Missing required production artifact"):
        runtime._load_json_file(tmp_path / "missing.json")


def test_load_json_file_rejects_invalid_shape(tmp_path):
    runtime = canonical_runtime.CanonicalRuntime()
    path = tmp_path / "invalid.json"
    path.write_text('["invalid"]', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid production artifact shape"):
        runtime._load_json_file(path)


def test_resolve_evidence_accepts_prebuilt_evidence():
    runtime = canonical_runtime.CanonicalRuntime()
    evidence = {"evidence_id": "EVIDENCE-1"}

    assert runtime._resolve_evidence({}, 1.0, evidence) == evidence


def test_resolve_evidence_fails_closed():
    runtime = canonical_runtime.CanonicalRuntime()

    with pytest.raises(ValueError, match="retrieval did not provide an evidence handle"):
        runtime._resolve_evidence({}, 1.0)


def test_execute_blocks_when_no_canonical_match(monkeypatch):
    runtime = canonical_runtime.CanonicalRuntime()

    monkeypatch.setattr(
        canonical_runtime,
        "retrieve_from_masterdb",
        lambda **_: {"best_record": {}, "confidence": 0.0},
    )

    result = runtime.execute(
        query="no canonical match",
        student_id="T_GOV_NO_MATCH",
        grade=1,
        subject="Mathematics",
    )

    assert result["blocked"] is True
    assert result["verification_status"] == "BLOCKED"
    assert result["convergence_validated"] is False


def test_gate_rejects_unverified_provenance():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    record["source_lineage"]["provenance_status"] = "UNVERIFIED"

    with pytest.raises(ValueError, match="provenance_status"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_missing_authority_field():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    record["source_lineage"]["publisher"] = ""

    with pytest.raises(ValueError, match="publisher"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_missing_evidence():
    runtime = canonical_runtime.CanonicalRuntime()
    record, _ = valid_fixture()

    with pytest.raises(ValueError, match="no evidence handle"):
        runtime._validate_production_gates(record, {})


def test_gate_rejects_missing_lineage_field():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    evidence["chapter"] = ""

    with pytest.raises(ValueError, match="chapter"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_empty_pages():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    evidence["page_numbers"] = []

    with pytest.raises(ValueError, match="page_numbers"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_lineage_hash_mismatch():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    evidence["lineage_hash"] = "BAD"

    with pytest.raises(ValueError, match="lineage_hash mismatch"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_missing_source_hash():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    evidence["source_hash"] = ""

    with pytest.raises(ValueError, match="source_hash"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_source_hash_mismatch():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    evidence["source_hash"] = "BAD"

    with pytest.raises(ValueError, match="source_hash does not match"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_bad_manifest_status(monkeypatch):
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    manifest = runtime._canonical_manifest()
    manifest["validation_status"] = "PENDING"
    monkeypatch.setattr(runtime, "_canonical_manifest", lambda: manifest)

    with pytest.raises(ValueError, match="not ALL_VERIFIED"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_version_mismatch():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    record["version"] = "BAD"

    with pytest.raises(ValueError, match="version and curriculum_version differ"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_dataset_hash_mismatch(monkeypatch):
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    manifest = runtime._canonical_manifest()
    pack = runtime._knowledge_pack_manifest()
    pack["dataset_hash"] = "BAD"

    monkeypatch.setattr(runtime, "_canonical_manifest", lambda: manifest)
    monkeypatch.setattr(runtime, "_knowledge_pack_manifest", lambda: pack)

    with pytest.raises(ValueError, match="knowledge pack hash mismatch"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_missing_dataset_signature(monkeypatch):
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    manifest = runtime._canonical_manifest()
    manifest["dataset_signature"] = ""

    monkeypatch.setattr(runtime, "_canonical_manifest", lambda: manifest)

    with pytest.raises(ValueError, match="manifest signature missing"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_incomplete_constitution(monkeypatch):
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    constitution = runtime._constitution_metadata()
    constitution["safety_gates"] = [
        gate for gate in constitution["safety_gates"]
        if gate != "runtime_contract"
    ]

    monkeypatch.setattr(runtime, "_constitution_metadata", lambda: constitution)

    with pytest.raises(ValueError, match="required safety gates are incomplete"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_bad_failure_policy(monkeypatch):
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    constitution = runtime._constitution_metadata()
    constitution["failure_policy"] = "allow canonical execution"

    monkeypatch.setattr(runtime, "_constitution_metadata", lambda: constitution)

    with pytest.raises(ValueError, match="refusal policy is not enforced"):
        runtime._validate_production_gates(record, evidence)


def test_gate_rejects_missing_canonical_authority():
    runtime = canonical_runtime.CanonicalRuntime()
    record, evidence = valid_fixture()

    record["governance"]["canonical_authority_granted"] = False

    with pytest.raises(ValueError, match="canonical_authority_granted=False"):
        runtime._validate_production_gates(record, evidence)


def test_expected_lineage_hash_is_stable():
    runtime = canonical_runtime.CanonicalRuntime()
    _, evidence = valid_fixture()

    assert runtime._expected_lineage_hash(evidence) == runtime._expected_lineage_hash(evidence)


def test_constitutional_failure_is_contained(monkeypatch):
    runtime = canonical_runtime.CanonicalRuntime()
    record, _ = valid_fixture()

    monkeypatch.setattr(
        canonical_runtime,
        "retrieve_from_masterdb",
        lambda **_: {"best_record": record, "confidence": 1.0},
    )
    monkeypatch.setattr(
        runtime,
        "_validate_production_gates",
        lambda *_: None,
    )
    monkeypatch.setattr(
        canonical_runtime,
        "build_learning_intelligence",
        lambda *_: {
            "learning_outcome": "learn counting",
            "learning_gap": None,
            "learning_path_suggestion": None,
            "practice_recommendations": [],
            "remediation_recommendation": None,
        },
    )

    class FakeMasteryEngine:
        def __init__(self, student_id, grade):
            self.student_id = student_id
            self.grade = grade

        def record_exercise(self, **kwargs):
            return None

        def build_progress_state(self):
            return {
                "mastery_score": 0.0,
                "concept_strengths": {},
                "concept_weaknesses": {},
                "recommended_remediation": None,
                "learning_progress_state": {},
                "mastery_level": "beginner",
                "weak_areas": [],
            }

    class FailingRuleEngine:
        def evaluate(self, **kwargs):
            raise RuntimeError("constitutional test failure")

    monkeypatch.setattr(canonical_runtime, "MasteryEngine", FakeMasteryEngine)
    runtime._rule_engine = FailingRuleEngine()

    result = runtime.execute(
        query="What is counting?",
        student_id="T_GOV_CONSTITUTIONAL_ERROR",
        grade=1,
        subject="Mathematics",
    )

    assert result["constitutional_runtime"]["active"] is True
    assert result["constitutional_runtime"]["decision"] == "error"
    assert result["constitutional_runtime"]["enforced"] is False
