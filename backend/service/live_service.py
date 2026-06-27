import logging
import time
import asyncio
from typing import Dict, Any, Optional

from core.engine import RuleEngine
from enforcement.enforcement import UniGuruEnforcement
from reasoning.concept_resolver import ConceptResolver
from retrieval.retriever import retrieve_knowledge_with_trace, NO_KNOWLEDGE_ANSWER
from utils.rag_logger import log_final_answer, log_incoming_request

logger = logging.getLogger("uniguru.live")


class LiveUniGuruService:
    def __init__(self):
        self.engine = RuleEngine()
        self.enforcement = UniGuruEnforcement()
        self.concept_resolver = ConceptResolver()

    async def ask(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        allow_web_retrieval: bool = False,
    ) -> Dict[str, Any]:
        """Ultra-Fast Async Reasoning Engine with unified retrieval."""
        start_time = time.perf_counter()
        metadata = dict(context or {})
        metadata["session_id"] = session_id
        caller = metadata.get("caller")

        log_incoming_request(user_query, session_id=session_id, caller=caller)

        content, retrieval_trace = await asyncio.to_thread(retrieve_knowledge_with_trace, user_query)

        if content and retrieval_trace.get("match_found"):
            decision = await asyncio.to_thread(
                self.engine.evaluate,
                content=user_query,
                metadata={**metadata, "prefetched_content": content, "retrieval_trace": retrieval_trace},
                apply_enforcement=False,
            )
            data = decision.setdefault("data", {})
            data["response_content"] = content
            data["retrieval_trace"] = retrieval_trace
            decision["decision"] = "answer"
            decision["verification_status"] = str(retrieval_trace.get("verification_status") or "VERIFIED")
            decision["reason"] = f"Verified knowledge retrieved via {retrieval_trace.get('method')}"
        else:
            decision = await asyncio.to_thread(
                self.engine.evaluate,
                content=user_query,
                metadata=metadata,
                apply_enforcement=False,
            )

        sealed = await asyncio.to_thread(self.enforcement.validate_and_bind, decision)
        total_latency = (time.perf_counter() - start_time) * 1000
        sealed["total_latency_ms"] = round(total_latency, 2)

        response = self._build_contract_response(sealed, session_id=session_id, retrieval_trace=retrieval_trace)
        log_final_answer(
            user_query,
            str(response.get("answer") or ""),
            str(response.get("verification_status") or "UNVERIFIED"),
            float(response.get("confidence") or 0.0),
            str(response.get("source") or "none"),
        )
        return response

    def _build_contract_response(
        self,
        sealed: Dict[str, Any],
        session_id: Optional[str],
        retrieval_trace: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        data = sealed.get("data") or {}
        answer = str(data.get("response_content") or sealed.get("answer") or "").strip()
        if not answer or answer == NO_KNOWLEDGE_ANSWER:
            answer = str(data.get("response_content") or "").strip()

        decision_raw = str(sealed.get("decision") or "block").lower()
        if decision_raw in {"answer", "forward", "fallback"}:
            decision = "answer" if answer else "reject"
        elif decision_raw == "allow":
            decision = "answer" if answer else "reject"
        else:
            decision = "reject"

        trace = retrieval_trace or data.get("retrieval_trace") or {}
        confidence = float(trace.get("confidence") or 0.0)
        source = str(trace.get("method") or trace.get("source") or "hybrid")
        verification_status = str(sealed.get("verification_status") or "UNVERIFIED")

        if decision == "reject" and not answer:
            answer = "Knowledge not found in verified ontology."

        return {
            "decision": decision,
            "confidence": round(confidence, 2),
            "source": source,
            "answer": answer,
            "session_id": session_id,
            "reason": sealed.get("reason"),
            "verification_status": verification_status,
            "ontology_reference": sealed.get("ontology_reference") or {
                "concept_id": "retrieval::unified",
                "domain": "knowledge",
            },
            "reasoning_trace": {
                "sources_consulted": trace.get("sources_consulted") or [source],
                "retrieval_confidence": confidence,
                "verification_status": verification_status,
                "similarity_scores": trace.get("similarity_scores") or [],
                "pipeline_trace": data.get("trace") or [],
            },
            "routing": {
                "route": "ROUTE_ONTOLOGY",
                "retrieval_method": source,
            },
            "governance_flags": sealed.get("governance_flags") or {},
            "enforcement_signature": sealed.get("enforcement_signature"),
            "request_id": sealed.get("request_id") or data.get("request_id"),
            "total_latency_ms": sealed.get("total_latency_ms"),
        }


live_service = LiveUniGuruService()
