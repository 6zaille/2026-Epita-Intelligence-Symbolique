"""Agent de synchronisation avec les sources Linked Data externes.

Aligne les entités locales (organisations, lieux, concepts) sur DBpedia et
Wikidata via une résolution par label (``rdfs:label`` / ``foaf:name`` /
``dct:title`` / ``skos:prefLabel``, insensible à la casse et aux accents). Les
correspondances produisent des liens ``owl:sameAs`` matérialisés dans
``urn:graph:links``.

Le liage s'appuie sur un **cache local** (``data/linked_data_cache/``) pour
rester reproductible hors-ligne. L'interrogation directe des endpoints SPARQL
publics de DBpedia/Wikidata (avec repli sur le cache) est une extension prévue
mais **non implémentée** à ce stade.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Dict, List

from rdflib import Graph, Namespace, OWL, RDF, RDFS, URIRef

from ..events import LINKING_COMPLETED, SemanticEvent
from .base import Agent

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DCT = Namespace("http://purl.org/dc/terms/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
EX = Namespace("http://epita.fr/scia/2026/g5/catalog#")
DBO = Namespace("http://dbpedia.org/ontology/")

#: garde de type POSITIVE : seuls les individus typés (asserté OU inféré) comme
#: entités nommables — agents/organisations/personnes/organismes publics,
#: concepts, lieux — sont candidats à un owl:sameAs. Une allowlist est plus sûre
#: qu'une simple exclusion des jeux de données/distributions : elle écarte AUSSI
#: les sujets NON typés, dont un titre homonyme d'une ressource DBpedia
#: provoquerait une fusion d'identités erronée. Limite connue : le cache local
#: ne type pas les entités distantes, donc la compatibilité de type
#: local↔distant n'est pas encore vérifiée (extension : typer le cache).
_LINKABLE_TYPES = (FOAF.Agent, FOAF.Organization, FOAF.Person,
                   EX.PublicBody, SKOS.Concept, DBO.Place, DBO.City)

_LABEL_PROPS = (RDFS.label, FOAF.name, DCT.title, SKOS.prefLabel)


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).casefold().strip()


class LinkingAgent(Agent):
    name = "LinkingAgent"
    handles = ("link",)

    def __init__(self, blackboard, cache_dir: Path) -> None:
        super().__init__(blackboard)
        self.remote_index: Dict[str, List[URIRef]] = {}
        for file in sorted(Path(cache_dir).glob("*.ttl")):
            g = Graph().parse(file)
            for prop in _LABEL_PROPS:
                for subject, label in g.subject_objects(prop):
                    self.remote_index.setdefault(_norm(str(label)), []).append(subject)

    def _execute(self, action: str, doc_uri: str) -> SemanticEvent:
        combined = self.blackboard.combined_doc_graph(doc_uri)
        links_graph = self.blackboard.links_graph

        # Garde de type (cf. _LINKABLE_TYPES) : l'égalité de label ne fonde une
        # identité forte owl:sameAs que si le sujet local est typé comme entité
        # nommable. On aligne donc UNIQUEMENT les sujets dont le type (asserté ou
        # inféré : le graphe combiné inclut la clôture) figure dans l'allowlist.
        linkable = {s for t in _LINKABLE_TYPES for s in combined.subjects(RDF.type, t)}

        counted: set = set()      # sujets distincts comptés comme candidats
        links = 0
        seen_pairs = set()
        for prop in _LABEL_PROPS:
            for subject, label in combined.subject_objects(prop):
                if not isinstance(subject, URIRef) or subject not in linkable:
                    continue
                counted.add(subject)
                for remote in self.remote_index.get(_norm(str(label)), []):
                    if remote == subject or (subject, remote) in seen_pairs:
                        continue
                    # owl:sameAs est symétrique : un seul triplet par lien, pour
                    # que le compteur sameAsLinks corresponde au graphe produit.
                    links_graph.add((subject, OWL.sameAs, remote))
                    seen_pairs.add((subject, remote))
                    links += 1

        meta = self.blackboard.documents[doc_uri]
        meta.update(status="linked", sameas_links=links)
        return self.emit(LINKING_COMPLETED, doc_uri,
                         candidates=len(counted), sameAsLinks=links)
