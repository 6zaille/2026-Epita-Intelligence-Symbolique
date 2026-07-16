"""Protocole de communication inter-agents fondé sur des évènements sémantiques.

Chaque évènement émis par un agent est un citoyen de première classe du graphe
de connaissances partagé : il est décrit en RDF (vocabulaire ``ag:``) et
persisté dans le graphe nommé ``urn:graph:events`` du blackboard. Les agents et
l'orchestrateur communiquent donc *via* le graphe, ce qui rend l'historique du
pipeline entièrement interrogeable en SPARQL (auditabilité, provenance).
"""

from __future__ import annotations

import itertools
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List

from rdflib import Literal, Namespace, RDF, URIRef, XSD

AG = Namespace("http://epita.fr/scia/2026/g5/agents#")
EV = Namespace("urn:events:")

# Types d'évènements sémantiques du protocole
DOCUMENT_INGESTED = "DocumentIngested"
EXTRACTION_COMPLETED = "ExtractionCompleted"
EXTRACTION_FAILED = "ExtractionFailed"
VALIDATION_SUCCEEDED = "ValidationSucceeded"
VIOLATION_DETECTED = "ViolationDetected"
TRIPLES_INFERRED = "TriplesInferred"
INCONSISTENCY_DETECTED = "InconsistencyDetected"
LINKING_COMPLETED = "LinkingCompleted"
INDEXING_COMPLETED = "IndexingCompleted"
DOCUMENT_PUBLISHED = "DocumentPublished"
DOCUMENT_QUARANTINED = "DocumentQuarantined"

_seq = itertools.count()


@dataclass
class SemanticEvent:
    """Évènement sémantique échangé entre agents."""

    type: str                      # p.ex. "ViolationDetected"
    emitter: str                   # nom de l'agent émetteur
    document: str                  # URI du document concerné
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: f"{next(_seq):05d}-{uuid.uuid4().hex[:8]}")

    @property
    def uri(self) -> URIRef:
        return EV[self.event_id]

    def to_triples(self):
        """Sérialise l'évènement en triplets RDF (protocole sémantique)."""
        s = self.uri
        yield (s, RDF.type, AG[self.type])
        yield (s, AG.emittedBy, AG[self.emitter])
        yield (s, AG.concernsDocument, URIRef(self.document))
        yield (s, AG.timestamp, Literal(self.timestamp, datatype=XSD.double))
        for key, value in self.payload.items():
            if isinstance(value, (int, float, str, bool)):
                yield (s, AG[key], Literal(value))
            else:
                # payload non scalaire : sérialisé en chaîne pour préserver
                # l'auditabilité (aucun payload structuré n'est émis à ce jour)
                yield (s, AG[key], Literal(str(value)))

    def __repr__(self) -> str:  # pragma: no cover - lisibilité des logs
        return f"<{self.type} doc={self.document.rsplit(':', 1)[-1]} by={self.emitter} {self.payload}>"


class EventBus:
    """Journal d'évènements sémantiques.

    Chaque évènement publié est (1) conservé dans un log en mémoire et (2)
    matérialisé en RDF dans le graphe ``urn:graph:events`` du blackboard
    attaché. Le bus est un **journal passif** : il n'orchestre rien. Le
    séquencement des agents est assuré par l'orchestrateur (``orchestrator.py``),
    qui réagit à la valeur de retour de chaque action ; les évènements servent
    la traçabilité et l'auditabilité SPARQL, pas le contrôle du flux.
    """

    def __init__(self) -> None:
        self._log: List[SemanticEvent] = []
        self._blackboard = None  # attaché par le Blackboard lui-même

    def attach_blackboard(self, blackboard) -> None:
        self._blackboard = blackboard

    def publish(self, event: SemanticEvent) -> SemanticEvent:
        self._log.append(event)
        if self._blackboard is not None:
            self._blackboard.record_event(event)
        return event

    @property
    def log(self) -> List[SemanticEvent]:
        return list(self._log)
