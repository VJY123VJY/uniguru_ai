"""
Canonical Sanskrit Registry.

Maintains the registry of immutable Sanskrit concepts used
by the UniGuru Sanskrit Ontology.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .schema import (
    SanskritConcept,
    sanskrit_concept_to_dict,
)


class SanskritRegistry:
    """
    Registry for Canonical Sanskrit Concepts.

    The registry guarantees deterministic concept lookup
    and stable canonical identifiers.
    """

    def __init__(self):

        self._concepts: Dict[str, SanskritConcept] = {}

    def register(
        self,
        concept: SanskritConcept,
    ) -> None:
        """
        Register a new Sanskrit concept.

        Existing concept IDs cannot be overwritten.
        """

        if concept.concept_id in self._concepts:
            raise ValueError(
                f"Concept already registered: {concept.concept_id}"
            )

        self._concepts[concept.concept_id] = concept

    def get(
        self,
        concept_id: str,
    ) -> SanskritConcept:
        """
        Retrieve a concept by its canonical ID.
        """

        if concept_id not in self._concepts:
            raise ValueError(
                f"Unknown Sanskrit concept: {concept_id}"
            )

        return self._concepts[concept_id]

    def exists(
        self,
        concept_id: str,
    ) -> bool:

        return concept_id in self._concepts

    def remove(
        self,
        concept_id: str,
    ) -> None:
        """
        Registry concepts are immutable.
        Removal is prohibited.
        """

        raise ValueError(
            "Canonical Sanskrit Concepts are immutable."
        )

    def update(
        self,
        concept: SanskritConcept,
    ) -> None:
        """
        Registry concepts are immutable.
        Updates are prohibited.
        """

        raise ValueError(
            "Canonical Sanskrit Concepts are immutable."
        )

    def list_concepts(self) -> List[SanskritConcept]:

        return list(self._concepts.values())

    def export_registry(self) -> List[Dict]:

        return [
            sanskrit_concept_to_dict(concept)
            for concept in self._concepts.values()
        ]


__all__ = [
    "SanskritRegistry",
]