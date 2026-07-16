"""Graphe de connaissances partagé (architecture blackboard).

Le blackboard est un ``rdflib.Dataset`` structuré en graphes nommés :

* ``urn:graph:doc:<id>``        : triplets extraits pour chaque document ;
* ``urn:graph:inferred:<id>``   : triplets *inférés* par raisonnement OWL-RL ;
* ``urn:graph:events``          : journal RDF des évènements sémantiques ;
* ``urn:graph:reports``         : rapports de validation SHACL ;
* ``urn:graph:links``           : liens owl:sameAs vers le Linked Data ;
* ``urn:graph:ontology``        : ontologie de domaine (TBox) partagée.

Tous les agents lisent et écrivent dans ce même espace de connaissances ; les
évènements sémantiques y sont journalisés (cf. ``events.py``) tandis que le
séquencement des agents est assuré par l'orchestrateur (cf. ``orchestrator.py``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

from rdflib import Dataset, Graph, URIRef

from .events import EventBus, SemanticEvent

DOC_NS = "urn:graph:doc:"
INF_NS = "urn:graph:inferred:"
EVENTS_GRAPH = URIRef("urn:graph:events")
REPORTS_GRAPH = URIRef("urn:graph:reports")
LINKS_GRAPH = URIRef("urn:graph:links")
ONTOLOGY_GRAPH = URIRef("urn:graph:ontology")


class Blackboard:
    """Espace de connaissances partagé entre les agents."""

    def __init__(self, bus: Optional[EventBus] = None) -> None:
        self.dataset = Dataset()
        self.bus = bus or EventBus()
        self.bus.attach_blackboard(self)
        self.documents: Dict[str, dict] = {}  # métadonnées de suivi par document

    # ------------------------------------------------------------------ docs
    def register_document(self, doc_id: str, path: Path) -> str:
        doc_uri = f"urn:doc:{doc_id}"
        self.documents[doc_uri] = {"id": doc_id, "path": Path(path), "status": "raw"}
        return doc_uri

    def doc_graph(self, doc_uri: str) -> Graph:
        return self.dataset.graph(URIRef(DOC_NS + doc_uri.rsplit(":", 1)[-1]))

    def inferred_graph(self, doc_uri: str) -> Graph:
        return self.dataset.graph(URIRef(INF_NS + doc_uri.rsplit(":", 1)[-1]))

    def combined_doc_graph(self, doc_uri: str) -> Graph:
        """Graphe asserté + inféré d'un document (vue matérialisée)."""
        g = Graph()
        for t in self.doc_graph(doc_uri):
            g.add(t)
        for t in self.inferred_graph(doc_uri):
            g.add(t)
        return g

    # ------------------------------------------------------- graphes globaux
    @property
    def ontology(self) -> Graph:
        return self.dataset.graph(ONTOLOGY_GRAPH)

    @property
    def events_graph(self) -> Graph:
        return self.dataset.graph(EVENTS_GRAPH)

    @property
    def reports_graph(self) -> Graph:
        return self.dataset.graph(REPORTS_GRAPH)

    @property
    def links_graph(self) -> Graph:
        return self.dataset.graph(LINKS_GRAPH)

    def load_ontology(self, path: Path) -> int:
        self.ontology.parse(path)
        return len(self.ontology)

    # ------------------------------------------------------------ évènements
    def record_event(self, event: SemanticEvent) -> None:
        g = self.events_graph
        for triple in event.to_triples():
            g.add(triple)

    # ----------------------------------------------------------------- SPARQL
    def query(self, sparql: str, doc_uri: Optional[str] = None):
        """Requête SPARQL sur un document ou sur l'union des connaissances."""
        if doc_uri is not None:
            return self.combined_doc_graph(doc_uri).query(sparql)
        union = Graph()
        for ctx in self.dataset.graphs():
            if ctx.identifier == EVENTS_GRAPH:
                continue
            for t in ctx:
                union.add(t)
        return union.query(sparql)

    # ------------------------------------------------------------- stats/util
    def stats(self) -> dict:
        per_graph = {str(c.identifier): len(c) for c in self.dataset.graphs()}
        return {
            "graphs": len(per_graph),
            "total_triples": sum(per_graph.values()),
            "per_graph": per_graph,
        }
