from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)

class SovereignRetriever:
    """
    Sovereign Retrieval Engine for UniGuru.
    Operates on the structured index in knowledge/index/
    """
    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "knowledge", "index", "master_index.json")
        )
        self.index: Dict[str, Any] = {}
        self._load_index()

    def _load_index(self) -> None:
        if not os.path.exists(self.index_path):
            logger.warning("KB index not found at %s. Running with empty index.", self.index_path)
            self.index = {}
            return
        try:
            with open(self.index_path, "r", encoding="utf-8-sig") as handle:
                raw = handle.read()
            try:
                loaded = json.loads(raw)
            except json.JSONDecodeError:
                # Repair legacy Windows paths with invalid JSON escapes (e.g. \density)
                repaired = re.sub(r"\\(?![\\\"/bfnrtu])", "/", raw)
                loaded = json.loads(repaired)
            if isinstance(loaded, dict):
                self.index = loaded
                logger.info("Sovereign index loaded with %s keywords.", len(self.index))
                return
            logger.warning("KB index at %s is not a JSON object. Running with empty index.", self.index_path)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load KB index (%s). Running with empty index.", exc)
        self.index = {}

    def _calculate_confidence(self, query: str, keyword: str) -> float:
        """
        Calculates confidence based on keyword coverage in query tokens.
        """
        query_tokens = set(re.sub(r"[^\w\s]", "", query.lower()).split())
        kw_tokens = set(keyword.split())

        if not kw_tokens:
            return 0.0

        matched = kw_tokens.intersection(query_tokens)
        return len(matched) / len(kw_tokens) if len(kw_tokens) > 0 else 0.0

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point for retrieval.
        Returns a structured response with source trace.
        """
        query_lower = user_query.lower()
        query_tokens = set(re.sub(r"[^\w\s]", "", query_lower).split())
        best_match = None
        highest_confidence = 0.0

        sorted_keywords = sorted(self.index.keys(), key=len, reverse=True)

        for kw in sorted_keywords:
            kw_lower = kw.lower()
            if kw_lower in query_lower or any(token in kw_lower for token in query_tokens if len(token) > 3):
                conf = self._calculate_confidence(user_query, kw)
                if kw_lower in query_lower:
                    conf = max(conf, 0.5)
                if conf > highest_confidence:
                    highest_confidence = conf
                    best_match = kw

        # Fallback: scan index entries for token overlap in content
        if not best_match or highest_confidence < 0.3:
            for kw, entry_list in self.index.items():
                if not isinstance(entry_list, list) or not entry_list:
                    continue
                entry = entry_list[0]
                content = str(entry.get("content") or "").lower()
                overlap = sum(1 for t in query_tokens if len(t) > 2 and t in content)
                if overlap == 0:
                    continue
                conf = overlap / max(len(query_tokens), 1)
                if conf > highest_confidence:
                    highest_confidence = conf
                    best_match = kw

        if best_match and highest_confidence >= 0.25:
            entry_list = self.index.get(best_match) or []
            entry = entry_list[0] if isinstance(entry_list, list) and entry_list else {}
            content = str(entry.get("content") or "")
            meta = entry.get("metadata") if isinstance(entry, dict) else {}
            if not isinstance(meta, dict):
                meta = {}
            return {
                "answer": content,
                "source_file": meta.get("source"),
                "author": meta.get("author"),
                "publication": meta.get("publication"),
                "confidence_level": round(highest_confidence, 2),
                "verified": bool(content),
            }

        return {
            "answer": "I do not have verified knowledge to answer this question.",
            "source_file": None,
            "confidence_level": 0.0,
            "verified": False,
        }


# Singleton for easy access
_engine = SovereignRetriever()


def retrieve(query: str) -> Dict[str, Any]:
    return _engine.query(query)
