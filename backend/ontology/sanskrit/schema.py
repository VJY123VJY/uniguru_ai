"""
Canonical Sanskrit Concept Schema.

Defines immutable Sanskrit semantic concepts used by
the UniGuru ontology subsystem.

This schema preserves deterministic execution,
semantic stability, and replay compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


REQUIRED_SANSKRIT_FIELDS = {
    "concept_id",
    "canonical_name",
    "sanskrit",
    "transliteration",
    "shabda",
    "dhatu",
    "vyakarana",
    "nirukta",
    "beeja",
    "tattva",
    "shakti",
    "functional_meaning",
    "related_concepts",
    "ontology_version",
    "semantic_version",
}


@dataclass(frozen=True)
class SanskritConcept:
    """
    Canonical Sanskrit Semantic Concept.

    Extends the UniGuru ontology with Sanskrit-specific
    semantic information while preserving deterministic
    execution and replay compatibility.
    """

    concept_id: str
    canonical_name: str

    sanskrit: str
    transliteration: str

    shabda: str
    dhatu: str
    vyakarana: str
    nirukta: str

    beeja: Optional[str]
    tattva: Optional[str]
    shakti: Optional[str]

    functional_meaning: str

    related_concepts: List[str]

    ontology_version: str
    semantic_version: str


def _validate_non_empty_string(value: Any, field_name: str) -> None:
    """Validate that a field is a non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def validate_sanskrit_concept_dict(data: Dict[str, Any]) -> None:
    """
    Validate a Sanskrit Concept dictionary against
    the canonical schema.
    """

    keys = set(data.keys())

    if keys != REQUIRED_SANSKRIT_FIELDS:
        missing = sorted(REQUIRED_SANSKRIT_FIELDS - keys)
        extra = sorted(keys - REQUIRED_SANSKRIT_FIELDS)

        raise ValueError(
            f"Sanskrit Concept schema mismatch. "
            f"Missing={missing or '[]'} "
            f"Extra={extra or '[]'}"
        )

    # Required string fields
    required_strings = [
        "concept_id",
        "canonical_name",
        "sanskrit",
        "transliteration",
        "shabda",
        "dhatu",
        "vyakarana",
        "nirukta",
        "functional_meaning",
        "ontology_version",
        "semantic_version",
    ]

    for field in required_strings:
        _validate_non_empty_string(data[field], field)

    # Optional semantic layers
    for field in ("beeja", "tattva", "shakti"):
        value = data[field]

        if value is not None and not isinstance(value, str):
            raise ValueError(f"{field} must be a string or None.")

    # Related Concepts
    if not isinstance(data["related_concepts"], list):
        raise ValueError("related_concepts must be a list.")

    for concept in data["related_concepts"]:
        if not isinstance(concept, str):
            raise ValueError(
                "related_concepts must contain only strings."
            )


def sanskrit_concept_from_dict(
    data: Dict[str, Any],
) -> SanskritConcept:
    """
    Create a SanskritConcept object
    from a validated dictionary.
    """

    validate_sanskrit_concept_dict(data)

    return SanskritConcept(
        concept_id=data["concept_id"],
        canonical_name=data["canonical_name"],
        sanskrit=data["sanskrit"],
        transliteration=data["transliteration"],
        shabda=data["shabda"],
        dhatu=data["dhatu"],
        vyakarana=data["vyakarana"],
        nirukta=data["nirukta"],
        beeja=data["beeja"],
        tattva=data["tattva"],
        shakti=data["shakti"],
        functional_meaning=data["functional_meaning"],
        related_concepts=data["related_concepts"],
        ontology_version=data["ontology_version"],
        semantic_version=data["semantic_version"],
    )


def sanskrit_concept_to_dict(
    concept: SanskritConcept,
) -> Dict[str, Any]:
    """
    Convert a SanskritConcept object
    into a dictionary.
    """

    return {
        "concept_id": concept.concept_id,
        "canonical_name": concept.canonical_name,
        "sanskrit": concept.sanskrit,
        "transliteration": concept.transliteration,
        "shabda": concept.shabda,
        "dhatu": concept.dhatu,
        "vyakarana": concept.vyakarana,
        "nirukta": concept.nirukta,
        "beeja": concept.beeja,
        "tattva": concept.tattva,
        "shakti": concept.shakti,
        "functional_meaning": concept.functional_meaning,
        "related_concepts": concept.related_concepts,
        "ontology_version": concept.ontology_version,
        "semantic_version": concept.semantic_version,
    }


__all__ = [
    "SanskritConcept",
    "validate_sanskrit_concept_dict",
    "sanskrit_concept_from_dict",
    "sanskrit_concept_to_dict",
]