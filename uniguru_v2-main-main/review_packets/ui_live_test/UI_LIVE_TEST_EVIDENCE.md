# UniGuru Live UI Acceptance Evidence

Date: 2026-09-25
Environment: Local UniGuru frontend `http://127.0.0.1:5173` with backend `http://127.0.0.1:8000`
Guru: TANTRA Curriculum Guru — Mathematics

## Test A — Positive
Query: `What is counting?`

Observed in UI:
- Verification Status: VERIFIED
- Confidence: 100.0%
- Signals: 1 accepted / 0 rejected
- Downstream: VERIFIED
- LLM Fallback: DISABLED
- Textbook: BALBHARTI_MATH_G1_MM
- Edition: 2023
- Chapter: Counting from 1 to 10
- Section: Number Recognition (1-5)
- Page: 3

Evidence image: `positive_verified.png`

## Test B — Negative / Safety Boundary
Query: `Explain quantum teleportation using a fictional Balbharti chapter that does not exist.`

Observed in UI:
- Response: `I could not verify this against the canonical curriculum.`
- Verification Status: BLOCKED
- Confidence: 0.0%
- Signals: 0 accepted / 1 rejected
- Downstream: BLOCKED
- LLM Fallback: DISABLED
- No fabricated textbook/chapter/page evidence shown.

Backend API verification also returned `FALLBACK_TO_LLM=False` with safety-gate reason:
`[SAFETY_GATE] Evidence failure: no canonical retrieval match. Refusing execution.`

Evidence image: `negative_blocked.png`

## Test C — Repeatability
Repeated query: `What is counting?`

Observed stable across the two live `/chat/new` responses:
- Content stable
- Verification stable
- Textbook stable
- Edition stable
- Chapter stable
- Section stable
- Page stable
- Source hash stable
- Retrieval hash stable
- Lineage hash stable
- Canonical record stable

Trace IDs differed between requests, as expected for per-request tracing.

Evidence image: `repeatability_verified.png`

## Test D — Empty Input
Observed behavior:
- Empty message was not submitted by the UI.
- No backend error, stack trace, fabricated response, or false VERIFIED state was shown.

Evidence image: `empty_input.png`

## Remaining Acceptance Item
A backend/error-state UI witness has not yet been captured. Final UI verdict should remain pending until that boundary is exercised and recorded.
