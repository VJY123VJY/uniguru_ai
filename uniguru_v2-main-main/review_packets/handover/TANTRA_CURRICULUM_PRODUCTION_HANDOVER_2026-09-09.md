\# TANTRA Curriculum Intelligence Runtime - Production Deployment \& Observer Handover



Date: 2026-09-09

Owner: Sanskar

Capability: tantra.curriculum\_intelligence

Version: 1.0.0

Schema: TANTRA\_CURRICULUM\_INTELLIGENCE\_CAPABILITY\_V1

Provider: TANTRA

Consumer: UniGuru



\## 1. Repository Baseline



Repository:

https://github.com/VJY123VJY/uniguru\_ai.git



Validated commit:



259f4a23011fee6ef1b0a49a7b96ca3b17aba927



Commit:

docs: add TANTRA curriculum runtime validation evidence



The validated runtime implementation and evidence are present on this commit.



\## 2. Runtime Contract



Application runtime:



Python 3.12

FastAPI

Uvicorn



Application entrypoint:



service.api:app



Expected bind:



0.0.0.0:8000



Startup command:



uvicorn service.api:app --host 0.0.0.0 --port 8000



Dependency source:



backend/requirements.txt



\## 3. TANTRA Capability Contract



Capability ID:



tantra.curriculum\_intelligence



Capability version:



1.0.0



Capability schema:



TANTRA\_CURRICULUM\_INTELLIGENCE\_CAPABILITY\_V1



Execution mode:



deterministic



Evidence required:



true



Replay safe:



true



Canonical runtime:



learning\_runtime.canonical\_runtime.execute\_query



Consumer:



UniGuru



The existing TANTRA CI workflow machine-validates this capability contract and its positive/negative execution paths.



\## 4. Required Production API Probes



The deployed FastAPI service must expose:



GET /health

GET /ready

GET /health/live



Curriculum execution endpoint:



POST /ask



\## 5. Positive TANTRA Production Validation



Request:



What is counting?



Expected result:



verification\_status = VERIFIED

convergence\_validated = true



Expected canonical evidence:



textbook\_id = BALBHARTI\_MATH\_G1\_MM

edition = 2023

chapter = Counting from 1 to 10

section = Number Recognition (1-5)

page\_numbers = \[3]



The response must preserve:



evidence\_id

source\_hash

retrieval\_hash

lineage\_hash



No unverified fallback may replace a governed curriculum result.



\## 6. Negative TANTRA Production Validation



Request:



Explain quantum teleportation using a fictional Balbharti chapter that does not exist



Expected result:



decision = block

verification\_status = BLOCKED

blocked = true

convergence\_validated = false

answer = null



Expected block reason must indicate failure of canonical retrieval/evidence and refusal of execution.



\## 7. Replay Determinism Validation



Execute the same positive request twice.



Compare:



evidence\_id

textbook\_id

source\_hash

retrieval\_hash

lineage\_hash

verification\_status



Expected result:



All identity/integrity fields match exactly and both executions remain VERIFIED.



\## 8. Production Safety Validation



The production deployment must preserve governed knowledge/curriculum failure behavior.



For a curriculum/knowledge execution failure:



\- no silent LLM downgrade

\- no fabricated curriculum evidence

\- no fabricated textbook identity

\- no synthetic evidence handles

\- no replacement of governed BLOCK responses with fallback answers



\## 9. Production Deployment Finding as of 2026-09-09



The public frontend domain currently resolves to:



https://www.uni-guru.in



Requests to /health, /ready, /health/live, /api/health, /api/ready, /docs, and /ask currently return the deployed frontend HTML rather than the current FastAPI API.



The repository's frontend production configuration currently references:



https://complete-uniguru.onrender.com



The observed Render service currently responds as an Express/Node service and returns "Not Found" for /, /api/v1/, /user/login, /ask, /ready, and /health/live.



Therefore the currently observed public deployment is not evidence of the FastAPI/TANTRA runtime described by this repository.



\## 10. Deployment Boundary



The repository does not contain a current render.yaml/render.yml deployment definition.



The current deployment mechanism for the validated FastAPI runtime is therefore externally managed and requires the production deployment owner/infrastructure environment.



No claim is made here that the target production environment has already deployed commit:



259f4a23011fee6ef1b0a49a7b96ca3b17aba927



\## 11. Required Infrastructure Action



Deploy the validated repository commit:



259f4a23011fee6ef1b0a49a7b96ca3b17aba927



using the Python/FastAPI runtime contract in this document.



Expose the FastAPI service through the approved production API hostname/path.



Do not substitute the currently observed Express Render service unless it is explicitly updated/reconfigured to serve the validated FastAPI application.



Do not change the TANTRA runtime contract to accommodate an unrelated legacy production service.



\## 12. Production Closure Criteria



Production validation can be marked PASS only after all of the following succeed in the target environment:



1\. Container/service startup.

2\. Service-to-service connectivity.

3\. Public/API accessibility.

4\. GET /health.

5\. GET /ready.

6\. GET /health/live.

7\. Positive POST /ask.

8\. Negative POST /ask.

9\. Replay determinism.

10\. Production configuration verification.

11\. Observer verification.



\## 13. Evidence References



Runtime implementation:



learning\_runtime/capability/curriculum\_intelligence.py



Canonical runtime:



learning\_runtime/canonical\_runtime.py



Fresh validation evidence:



review\_packets/proof\_logs/tantra\_runtime\_validation\_2026-09-09.json



Validation progress:



review\_packets/progress/TANTRA\_RUNTIME\_VALIDATION\_2026-09-09.md



TANTRA CI:



evidence\_packet/deployment\_proof/tantra-runtime-ci.yml



Deployment readiness:



evidence\_packet/deployment\_proof/deployment\_readiness.md



\## 14. Observer Verification



Observer:



Vijay Dhawan



Observer verification status:



PENDING



Observer must verify:



\- repository commit

\- capability metadata

\- deterministic execution

\- evidence preservation

\- negative safety gate

\- replay behavior

\- target-environment deployment

\- production probes

\- production positive/negative execution



Observer decision:



PENDING



Observer notes:



PENDING



\## 15. Final Status



Runtime implementation:

PASS



Local/runtime validation:

PASS



Automated validation:

PASS



Capability contract:

PASS



Production target validation:

PENDING



Observer verification:

PENDING



This document intentionally does not claim successful production deployment before target-environment evidence exists.

