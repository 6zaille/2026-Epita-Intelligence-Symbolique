"""Agent de raisonnement OWL-RL.

Calcule la clôture déductive OWL-RL (bibliothèque *owlrl*) du graphe du
document augmenté de l'ontologie de domaine, puis matérialise dans le graphe
``urn:graph:inferred:<id>`` le *delta au niveau des individus du document*
(faits nouvellement inférés portant sur les ressources du document). La clôture
de la TBox elle-même (subsomptions/domaines/co-domaines entre termes de
l'ontologie), identique d'un document à l'autre, est exclue du compte : elle
n'apprend rien sur le document et gonflerait artificiellement le ratio.
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

#: axiomatique interne d'owlrl que l'on ne matérialise pas comme inférence du document
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

        # Matérialisation des inférences AU NIVEAU DES INDIVIDUS du document.
        # ``before`` contient déjà les faits assertés ET l'ontologie (capturé
        # après leur ajout), donc ``triple in before`` écarte l'un comme l'autre.
        # On exclut en outre :
        #  * la clôture de la TBox elle-même (subClassOf/domain/range/… entre
        #    termes de l'ontologie) : ces triplets ne disent rien du document,
        #    sont identiques d'un document à l'autre et gonfleraient le compte et
        #    le ratio ; on les reconnaît à un sujet déjà défini dans l'ontologie
        #    (classes, propriétés, noeuds anonymes de restriction) ;
        #  * le bruit de clôture OWL-RL : triplets réflexifs (X ⇔ X), typage
        #    owl:Thing/owl:Nothing, littéraux en position sujet, déclarations de
        #    datatypes et de propriétés d'annotation.
        onto_terms = set(self.blackboard.ontology.subjects())
        inferred_graph = self.blackboard.inferred_graph(doc_uri)
        new_count = 0
        for triple in work:
            if triple in before:
                continue
            s, p, o = triple
            if s in onto_terms:                       # clôture TBox (hors document)
                continue
            if s in _NOISE_SUBJECTS or o in _NOISE_SUBJECTS:
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
