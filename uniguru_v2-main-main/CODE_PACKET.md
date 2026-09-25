# T-GOV-F01 CODE PACKET

Task: T-GOV-F01
Validation date: 2026-09-23
Scope: uniguru_v2-main-main

## Canonical Runtime

Execution chain:
TANTRA capability adapter -> canonical runtime -> retrieval engine -> evidence-first retrieval -> learning intelligence -> mastery/constitutional runtime -> runtime contract

Source files:
- learning_runtime/capability/curriculum_intelligence.py
- learning_runtime/canonical_runtime.py
- retrieval/retrieval_engine.py
- retrieval/evidence_first_retrieval.py

## API Hardening

Implementation:
backend/service/api.py
backend/service/guru_models.py

Strict request models:
ChatCreateRequest
ChatUpdateRequest
ChatMessageRequest
GoogleOAuthTokenRequest
UserLoginRequest
UserSignupRequest
NewRagRequest
CoreRequest

All hardened models use ConfigDict(extra="forbid").

Boundary tests verify:
- unknown fields return HTTP 422
- invalid authentication remains HTTP 401

## Automated Tests

- backend/tests/test_api_request_contracts.py
- backend/tests/test_curriculum_determinism.py
- backend/tests/test_tgov_canonical_runtime_boundaries.py

## Determinism

50 consecutive executions were verified.

Canonical state SHA-256:
8391251826788e78ffcdfb58b5aaa3cfb684c73c33d2f01c17e9a13125296ffc

Runtime evidence SHA-256:
5b991c3cd29161bb506eaf0b49baf1c1db7e6b6ecb168d98f28cf19461e6babb

Result:
1 passed in 0.99s

## Coverage

canonical_runtime.py: 93%
curriculum_intelligence.py: 100%
evidence_first_retrieval.py: 91%
retrieval_engine.py: 87%

Combined T-GOV execution-chain coverage: 91%

## Regression

Full suite:
76 passed

## Dependencies

Manifest:
requirements.txt

Audit:
98 dependencies
0 unpinned or malformed

Pinned validation tooling:
pytest==9.0.3
pytest-cov==7.1.0
coverage==7.16.1
pytest-asyncio==1.4.0

## Acceptance Evidence

Full regression: PASS
50-run determinism: PASS
Combined T-GOV coverage: PASS (91%)
Dependency pinning: PASS
Strict inbound API schemas: PASS
Authentication error boundary: PASS

## Delivered Artifacts

backend/service/api.py
backend/tests/test_api_request_contracts.py
backend/tests/test_curriculum_determinism.py
backend/tests/test_tgov_canonical_runtime_boundaries.py
requirements.txt
REVIEW_PACKET.md
CODE_PACKET.md
CODE_INDEX.md

This packet documents the T-GOV-F01 remediation and local validation evidence obtained on 2026-09-23. It does not replace the historical Phase 1-6 review record.


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

### T-GOV Dependency Compatibility Validation

The mission prompt specifies pytest==9.0.3 with pytest-asyncio==0.24.0. That exact pair is dependency-incompatible because pytest-asyncio==0.24.0 requires a pytest version below 9.0. The validated compatible test-tooling pin is pytest-asyncio==1.4.0.

Isolated `.venv_tgov` validation:
- dependency resolution: PASS
- pip check: PASS
- full regression: 76 passed
- determinism: PASS
- focused T-GOV coverage: 45 passed, 91% total
