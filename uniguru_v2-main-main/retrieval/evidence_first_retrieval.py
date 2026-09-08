from __future__ import annotations

import json
import uuid
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List

def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class VerificationHandle:
    authority_status: str
    signature: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "authority_status": self.authority_status,
            "signature": self.signature,
            "timestamp": self.timestamp
        }

@dataclass(frozen=True)
class LineageHandle:
    textbook_id: str
    edition: str
    chapter: str
    section: str
    lineage_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "textbook_id": self.textbook_id,
            "edition": self.edition,
            "chapter": self.chapter,
            "section": self.section,
            "lineage_hash": self.lineage_hash
        }

@dataclass(frozen=True)
class PageHandle:
    page_number: int
    content_hash: str
    ocr_status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_number": self.page_number,
            "content_hash": self.content_hash,
            "ocr_status": self.ocr_status
        }

@dataclass(frozen=True)
class AuthorityHandle:
    publisher: str
    board: str
    isbn: str
    authority_signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "publisher": self.publisher,
            "board": self.board,
            "isbn": self.isbn,
            "authority_signature": self.authority_signature
        }

@dataclass(frozen=True)
class EvidenceHandle:
    evidence_id: str
    textbook_id: str
    edition: str
    chapter: str
    section: str
    page_numbers: List[int]
    source_hash: str
    retrieval_hash: str
    lineage_hash: str
    verification_status: str
    
    # Nested handles
    verification: VerificationHandle
    lineage: LineageHandle
    page: PageHandle
    authority: AuthorityHandle

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "textbook_id": self.textbook_id,
            "edition": self.edition,
            "chapter": self.chapter,
            "section": self.section,
            "page_numbers": self.page_numbers,
            "source_hash": self.source_hash,
            "retrieval_hash": self.retrieval_hash,
            "lineage_hash": self.lineage_hash,
            "verification_status": self.verification_status,
            "verification": self.verification.to_dict(),
            "lineage": self.lineage.to_dict(),
            "page": self.page.to_dict(),
            "authority": self.authority.to_dict()
        }

@dataclass(frozen=True)
class RetrievalResult:
    record: Dict[str, Any]
    score: float
    evidence: EvidenceHandle

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record": self.record,
            "score": self.score,
            "evidence": self.evidence.to_dict()
        }

def build_evidence_handle(
    record: Dict[str, Any],
    query: str,
    confidence: float,
) -> EvidenceHandle:
    """Build an evidence handle from canonical record evidence.

    The canonical ``evidence`` object is authoritative for evidence identity,
    textbook/edition lineage, page references, hashes, and verification status.

    Authority metadata is retained from the record's existing ``source_lineage``
    contract. No synthetic/default textbook, page, authority, or timestamp values
    are permitted.
    """
    del query
    del confidence

    record_id = record.get("record_id")
    if not record_id:
        raise ValueError("Canonical evidence requires record_id")

    canonical = record.get("evidence")
    if not isinstance(canonical, dict):
        raise ValueError(
            f"Canonical evidence missing for record_id={record_id}"
        )

    source_lineage = record.get("source_lineage")
    if not isinstance(source_lineage, dict):
        raise ValueError(
            f"Canonical source_lineage missing for record_id={record_id}"
        )

    # Canonical evidence fields.
    required_evidence_fields = (
        "evidence_id",
        "textbook_id",
        "edition",
        "chapter",
        "section",
        "page_numbers",
        "source_hash",
        "retrieval_hash",
        "lineage_hash",
        "verification_status",
    )

    missing = [
        field
        for field in required_evidence_fields
        if canonical.get(field) in (None, "", [])
    ]

    if missing:
        raise ValueError(
            f"Canonical evidence incomplete for record_id={record_id}: "
            f"missing {', '.join(missing)}"
        )

    page_numbers = canonical["page_numbers"]

    if (
        not isinstance(page_numbers, list)
        or not page_numbers
        or not all(isinstance(page, int) for page in page_numbers)
    ):
        raise ValueError(
            f"Canonical evidence has invalid page_numbers "
            f"for record_id={record_id}"
        )

    if canonical["verification_status"] != "VERIFIED":
        raise ValueError(
            f"Canonical evidence is not VERIFIED for record_id={record_id}"
        )

    textbook_id = canonical["textbook_id"]
    edition = str(canonical["edition"])
    chapter = canonical["chapter"]
    section = canonical["section"]
    source_hash = canonical["source_hash"]
    lineage_hash = canonical["lineage_hash"]
    evidence_id = canonical["evidence_id"]
    retrieval_hash = canonical["retrieval_hash"]

    # Verify canonical lineage integrity.
    expected_lineage = (
        f"{textbook_id}::{edition}::{chapter}::{section}::{page_numbers}"
    )
    expected_lineage_hash = stable_hash(expected_lineage)

    if lineage_hash != expected_lineage_hash:
        raise ValueError(
            f"Canonical lineage hash mismatch for record_id={record_id}"
        )

    # Evidence ID must remain deterministically bound to record_id.
    expected_evidence_id = str(
        uuid.uuid5(uuid.NAMESPACE_DNS, record_id)
    )

    if evidence_id != expected_evidence_id:
        raise ValueError(
            f"Canonical evidence_id mismatch for record_id={record_id}"
        )

    # Authority metadata lives in source_lineage in the existing
    # canonical dataset model. Require it; never synthesize it.
    required_authority_fields = (
        "publisher",
        "board",
        "isbn",
        "authority_signature",
        "verification_timestamp",
    )

    missing_authority = [
        field
        for field in required_authority_fields
        if source_lineage.get(field) in (None, "")
    ]

    if missing_authority:
        raise ValueError(
            f"Canonical authority metadata incomplete for "
            f"record_id={record_id}: missing "
            f"{', '.join(missing_authority)}"
        )

    publisher = source_lineage["publisher"]
    board = source_lineage["board"]
    isbn = source_lineage["isbn"]
    authority_signature = source_lineage["authority_signature"]
    verification_timestamp = source_lineage["verification_timestamp"]

    authority = AuthorityHandle(
        publisher=publisher,
        board=board,
        isbn=isbn,
        authority_signature=authority_signature,
    )

    page = PageHandle(
        page_number=page_numbers[0],
        content_hash=source_hash,
        ocr_status="VERIFIED",
    )

    lineage = LineageHandle(
        textbook_id=textbook_id,
        edition=edition,
        chapter=chapter,
        section=section,
        lineage_hash=lineage_hash,
    )

    verification = VerificationHandle(
        authority_status="VERIFIED_AUTHORITY",
        signature=authority_signature,
        timestamp=verification_timestamp,
    )

    return EvidenceHandle(
        evidence_id=evidence_id,
        textbook_id=textbook_id,
        edition=edition,
        chapter=chapter,
        section=section,
        page_numbers=list(page_numbers),
        source_hash=source_hash,
        retrieval_hash=retrieval_hash,
        lineage_hash=lineage_hash,
        verification_status=canonical["verification_status"],
        verification=verification,
        lineage=lineage,
        page=page,
        authority=authority,
    )