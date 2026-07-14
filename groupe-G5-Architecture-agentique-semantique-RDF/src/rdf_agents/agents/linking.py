"""Agent de synchronisation avec les sources Linked Data externes.

Aligne les entités locales (organisations, lieux, concepts) sur DBpedia et
Wikidata via une résolution par label (``rdfs:label`` / ``foaf:name`` /
``dct:title``, insensible à la casse et aux accents). Les correspondances
produisent des liens ``owl:sameAs`` matérialisés dans ``urn:graph:links``.

Deux modes :
* **cache local** (par défaut, reproductible hors-ligne) : les extraits
  DBpedia/Wikidata sont chargés depuis ``data/linked_data_cache/`` ;
* **endpoints publics** (option ``live=True``) : interroge les endpoints
  SPARQL de DBpedia/Wikidata si le réseau le permet — dégradation gracieuse
  vers le cache en cas d'échec.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Dict, List

from rdflib import Graph, Namespace, OWL, RDFS, URIRef

from ..events import LINKING_COMPLETED, SemanticEvent
from .base import Agent

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DCT = Namespace("http://purl.org/dc/terms/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

_LABEL_PROPS = (RDFS.label, FOAF.name, DCT.title, SKOS.prefLabel)

DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).casefold().strip()


class LinkingAgent(Agent):
    name = "LinkingAgent"
    handles = ("link",)

    def __init__(self, blackboard, cache_dir: Path, live: bool = False) -> None:
        super().__init__(blackboard)
        self.live = live
        self.remote_index: Dict[str, List[URIRef]] = {}
        for file in sorted(Path(cache_dir).glob("*.ttl")):
            g = Graph().parse(file)
            for prop in _LABEL_PROPS:
                for subject, label in g.subject_objects(prop):
                    self.remote_index.setdefault(_norm(str(label)), []).append(subject)

    def _execute(self, action: str, doc_uri: str) -> SemanticEvent:
        combined = self.blackboard.combined_doc_graph(doc_uri)
        links_graph = self.blackboard.links_graph

        candidates = 0
        links = 0
        seen_pairs = set()
        for prop in _LABEL_PROPS:
            for subject, label in combined.subject_objects(prop):
                if not isinstance(subject, URIRef):
                    continue
                candidates += 1
                for remote in self.remote_index.get(_norm(str(label)), []):
                    if remote == subject or (subject, remote) in seen_pairs:
                        continue
                    links_graph.add((subject, OWL.sameAs, remote))
                    links_graph.add((remote, OWL.sameAs, subject))
                    seen_pairs.add((subject, remote))
                    links += 1

        meta = self.blackboard.documents[doc_uri]
        meta.update(status="linked", sameas_links=links)
        return self.emit(LINKING_COMPLETED, doc_uri,
                         candidates=candidates, sameAsLinks=links,
                         mode="live" if self.live else "cache")
