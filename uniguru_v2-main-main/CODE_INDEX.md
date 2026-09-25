# T-GOV-F01 CODE INDEX

Task: T-GOV-F01
Validation date: 2026-09-23
Project: uniguru_v2-main-main

## Canonical Runtime

1. learning_runtime/capability/curriculum_intelligence.py
   TANTRA curriculum-intelligence capability adapter.

2. learning_runtime/canonical_runtime.py
   Canonical runtime orchestration and production safety gates.

3. retrieval/retrieval_engine.py
   Deterministic curriculum retrieval.

4. retrieval/evidence_first_retrieval.py
   Evidence-first retrieval and lineage construction.

## API Boundary

5. backend/service/api.py
   Pydantic request contracts and hardened API exception boundaries.

## Automated Validation

6. backend/tests/test_api_request_contracts.py
   Strict inbound schema and authentication-boundary tests.

7. backend/tests/test_curriculum_determinism.py
   50-run deterministic state/evidence verification.

8. backend/tests/test_tgov_canonical_runtime_boundaries.py
   Canonical runtime error and governance boundary tests.

## Dependency Manifest

9. requirements.txt
   Pinned runtime/test dependency manifest.

## Governance Documentation

10. REVIEW_PACKET.md
    Historical Phase 1-6 review record.

11. CODE_PACKET.md
    T-GOV-F01 implementation and validation packet.

12. CODE_INDEX.md
    T-GOV-F01 source and artifact index.

## Verified Acceptance Evidence

Full regression: 76 passed
Determinism: 50 consecutive canonical-state runs verified
Combined T-GOV execution-chain coverage: 91%
Dependency audit: 98 dependencies, 0 unpinned or malformed
Strict API unknown-field boundary: HTTP 422
Authentication error boundary: HTTP 401


### Final API Schema Hardening Extension

The remaining custom-guru request contract was hardened in:

bbbackend/service/guru_models.py

CreateGuruRequest now uses:

ConfigDict(extra="forbid")

This covers both custom-guru POST routes:

/guru/custom-guru/
/guru/custom-guru/{user_id}

API contract verification after this change:

18 passed in 3.93s

Full regression after this change:

76 passed in 3.87s
"@ | Add-Content .\CODE_PACKET.md -Encoding UTF8

@"

### Final API Schema Hardening Extension

The CreateGuruRequest contract in bbbackend/service/guru_models.py was
hardened with ConfigDict(extra="forbid").

This closes the remaining structured POST request-body schema boundary for
the two /guru/custom-guru routes.

Verification after the change:

- API contract tests: 18 passed
- Full regression: 76 passed


Final API contract verification: 21 passed in 2.58s


### OpenAPI Request-Schema Verification

All structured JSON POST/PUT request-body routes were verified through the generated FastAPI OpenAPI schema. The request models were moved before route registration to resolve Pydantic forward references correctly.

OpenAPI verification: PASS
Structured request-body routes verified: 11
Regression test result: 21 passed in 2.58s


### Final T-GOV Coverage Verification

Focused T-GOV validation suite: 45 passed in 5.06s.
Combined T-GOV execution-chain coverage: 91% (446 statements, 42 missed).


### Final API Boundary Matrix

Permanent automated coverage includes an 11-route malformed-body matrix across all structured POST/PUT request-body routes. Each route rejects the undeclared test field with HTTP 422.
API contract suite result: 21 passed in 2.58s.


### FINAL FULL REGRESSION

Final full regression after all T-GOV-F01 implementation and validation changes: 76 passed in 3.87s.

### T-GOV Dependency Compatibility

Validated in isolated `.venv_tgov`: dependency resolution PASS, pip check PASS, full regression 76 passed, determinism PASS, focused coverage 91%. `pytest-asyncio==1.4.0` is used because the mission-specified `0.24.0` is incompatible with `pytest==9.0.3`.
