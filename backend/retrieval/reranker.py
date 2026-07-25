import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RelevanceReranker:
    def __init__(self):
        pass

    def rerank_and_filter(self, candidates: List[Dict[str, Any]], expected_class: str = None, expected_subject: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks and filters the initial FAISS candidates.
        Enforces strict matching for class_level.
        """
        if not candidates:
            return []

        scored_candidates = []
        for candidate in candidates:
            score = candidate.get("score", 0.0)
            meta = candidate.get("metadata", {})
            
            cand_class = str(meta.get("class_level") or "").lower().strip()
            cand_subj = str(meta.get("subject") or "").lower().strip()

            penalty = 0.0
            is_valid = True

            # Strict filter for class mismatch
            if expected_class:
                expected_class = str(expected_class).lower().strip()
                if cand_class and cand_class != "none" and cand_class != "":
                    if expected_class != cand_class:
                        is_valid = False

            if expected_subject:
                expected_subject = str(expected_subject).lower().strip()
                if cand_subj and cand_subj != "none" and cand_subj != "":
                    if expected_subject not in cand_subj and cand_subj not in expected_subject:
                        penalty += 0.3 # Penalize but don't strictly filter out in case of synonym mismatch

            if is_valid:
                candidate["reranked_score"] = score - penalty
                scored_candidates.append(candidate)

        # Sort by the new reranked score
        scored_candidates.sort(key=lambda x: x.get("reranked_score", 0.0), reverse=True)
        return scored_candidates[:top_k]

reranker = RelevanceReranker()
