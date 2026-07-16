"""Agent de raisonnement OWL-RL.

Calcule la clôture déductive OWL-RL (bibliothèque *owlrl*) du graphe du
document augmenté de l'ontologie de domaine, puis matérialise le *delta*
(triplets nouvellement inférés) dans le graphe ``urn:graph:inferred:<id>``.
Les inférences sont donc traçables séparément des faits assertés.

L'agent détecte également les inconsistances : owlrl matérialise les
contradictions (p.ex. individu commun à deux classes disjointes, règle cax-dw)
sous forme d'un nœud d'erreur portant la propriété ``agent-ont#error`` ;
l'agent le convertit en ``InconsistencyDetected`` (mise en quarantaine du
document). Un individu inféré membre de ``owl:Nothing`` sert de filet secondaire.
"""

from __future__ import annotations

from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef

from ..events import INCONSISTENCY_DETECTED, TRIPLES_INFERRED, SemanticEvent
from .base import Agent

OWL = Namespace("http://www.w3.org/2002/07/owl#")
#: vocabulaire utilisé par owlrl pour matérialiser les contradictions
_ERR = Namespace("http://www.daml.org/2002/03/agents/agent-ont#")

#: axiomatique interne d'owlrl que l'on ne matérialise pas comme "inférence métier"
_NOISE_SUBJECTS = {OWL.Nothing, OWL.Thing}


class ReasoningAgent(Agent):
    name = "ReasoningAgent"
    handles = ("reason",)

    def _execute(self, action: str, doc_uri: str) -> SemanticEvent:
        asserted = self.blackboard.doc_graph(doc_uri)

        work = Graph()
        for t in asserted:
            work.add(t)
        for t in self.blackboard.ontology:
            work.add(t)
        before = set(work)

        DeductiveClosure(OWLRL_Semantics, axiomatic_triples=False,
                         datatype_axioms=False).expand(work)

        # Détection d'inconsistance : owlrl matérialise les contradictions
        # (p.ex. individu commun à deux classes disjointes, règle cax-dw)
        # sous forme de noeuds ErrorMessage ; on relève aussi tout individu
        # inféré membre de owl:Nothing.
        errors = [str(o) for _, o in work.subject_objects(_ERR.error)]
        errors += [f"{s} rdf:type owl:Nothing"
                   for s in work.subjects(RDF.type, OWL.Nothing)
                   if isinstance(s, URIRef) and s not in _NOISE_SUBJECTS]
        if errors:
            self.blackboard.documents[doc_uri]["status"] = "failed"
            return self.emit(INCONSISTENCY_DETECTED, doc_uri,
                             details="; ".join(sorted(errors)[:3]),
                             count=len(errors))

        # Matérialisation du *delta métier* : ``before`` contient déjà les faits
        # assertés ET l'ontologie (capturé après leur ajout), donc ``triple in
        # before`` suffit à écarter l'un comme l'autre. On exclut en plus le
        # bruit de clôture OWL-RL qui gonflerait artificiellement le ratio
        # d'inférence sans rien apprendre sur le document : triplets réflexifs
        # (X ⇔ X), littéraux en position sujet (RDF invalide), déclarations de
        # datatypes et de propriétés d'annotation.
        inferred_graph = self.blackboard.inferred_graph(doc_uri)
        new_count = 0
        for triple in work:
            if triple in before:
                continue
            s, p, o = triple
            if s in _NOISE_SUBJECTS or o in _NOISE_SUBJECTS or p == _ERR.error:
                continue
            if s == o:
                continue
            if isinstance(s, Literal):
                continue
            if p == RDF.type and o in (RDFS.Datatype, OWL.AnnotationProperty):
                continue
            inferred_graph.add(triple)
            new_count += 1

        meta = self.blackboard.documents[doc_uri]
        meta.update(status="enriched", inferred=new_count)
        ratio = new_count / max(len(asserted), 1)
        return self.emit(TRIPLES_INFERRED, doc_uri,
                         inferredTriples=new_count,
                         assertedTriples=len(asserted),
                         inferenceRatio=round(ratio, 3))
