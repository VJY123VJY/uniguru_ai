# TANTRA Curriculum Intelligence - Integration

## 1. Purpose

This document describes how the reusable TANTRA Curriculum Intelligence capability is attached to and consumed by the existing UniGuru runtime.

The integration does not introduce a separate UniGuru-specific curriculum implementation.

## 2. Capability Registration

| Property | Value |
|---|---|
| Capability ID | tantra.curriculum_intelligence |
| Version | 1.0.0 |
| Schema | TANTRA_CURRICULUM_INTELLIGENCE_CAPABILITY_V1 |
| Provider | TANTRA |
| Domain | curriculum_intelligence |
| Consumer | UniGuru |
| Execution mode | deterministic |
| Evidence required | true |
| Replay safe | true |

Canonical runtime:

learning_runtime.canonical_runtime.execute_query

## 3. Canonical Runtime API

The validated execution surface is:

learning_runtime.canonical_runtime.execute_query

## 4. Input

Validated runtime input includes:

- query
- student_id
- grade
- subject

The runtime can use curriculum context including medium and canonical curriculum metadata where applicable.

## 5. Successful Response

A successful supported curriculum request returns:

verification_status = VERIFIED

The validated positive response also contains:

- evidence identity
- textbook identity
- chapter
- section
- page information
- source hash
- retrieval hash
- lineage hash
- retrieval match
- retrieval confidence
- curriculum intelligence
- learning intelligence
- constitutional runtime state
- pipeline trace
- pipeline stages

## 6. Evidence Contract

The validated evidence structure includes:

- evidence_id
- textbook_id
- edition
- chapter
- section
- page_numbers
- source_hash
- retrieval_hash
- lineage_hash
- verification_status

The positive runtime additionally preserves authority and provenance information.

## 7. Failure Contract

When canonical curriculum evidence cannot be retrieved, the runtime blocks execution.

Expected governed state:

verification_status = BLOCKED
blocked = true
convergence_validated = false

The block reason identifies canonical evidence failure.

The runtime does not silently convert the unsupported curriculum request into an unverified curriculum answer.

## 8. Positive Integration Example

Request:

What is counting?

Context:

student_id = TANTRA_FINAL_POSITIVE_001
grade = 1
subject = Mathematics

Observed result:

verification_status = VERIFIED
convergence_validated = true
retrieval.matched = true
retrieval.confidence = 1.0

Resolved curriculum:

Textbook: BALBHARTI_MATH_G1_MM
Chapter: Counting from 1 to 10
Section: Number Recognition (1-5)
Page: 3

## 9. Negative Integration Example

Request:

Explain quantum teleportation using a fictional Balbharti chapter that does not exist

Observed result:

verification_status = BLOCKED
blocked = true
convergence_validated = false

Block reason:

[SAFETY_GATE] Evidence failure: no canonical retrieval match. Refusing execution.

## 10. UniGuru Integration Boundary

The validated architecture is:

Student Query
->
UniGuru Router
->
TANTRA Curriculum Intelligence
->
Canonical Retrieval
->
Evidence / Verification
->
Learning Intelligence
->
Mastery Intelligence
->
Constitutional Runtime
->
Runtime Contract

The HTTP /ask integration preserves governed curriculum blocks.

The validated unsupported request retained:

decision = block
verification_status = BLOCKED
status_action = BLOCK

## 11. CI Validation

The repository contains:

.github/workflows/tantra-runtime-ci.yml

The workflow validates:

- dependency installation
- automated tests
- TANTRA capability metadata
- positive curriculum runtime
- negative safety gate
- repository whitespace

The CI workflow was pushed to the repository and reached a green state during validation.

## 12. Deployment Considerations

Container deployment artifacts include:

Dockerfile
docker-compose.yml

The deployment proof package is stored under:

evidence_packet/deployment_proof/

The deployment topology includes:

Nginx
->
Node Backend
->
UniGuru API

Target-environment production validation remains pending.

## 13. Integration Safety

The integration must preserve the canonical evidence boundary.

Future consumers should attach to:

tantra.curriculum_intelligence

rather than implementing a second curriculum intelligence path.
