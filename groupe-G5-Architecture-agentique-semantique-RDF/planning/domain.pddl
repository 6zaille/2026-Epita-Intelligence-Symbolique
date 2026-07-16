;; Domaine PDDL du pipeline de traitement de documents RDF.
;; Chaque action correspond à l'invocation d'un agent spécialisé par
;; l'orchestrateur. La planification détermine l'ordonnancement des agents
;; en fonction de l'état du document (type, besoin de liage, échec...).

(define (domain rdf-pipeline)
  (:requirements :strips :typing :negative-preconditions)
  (:types document)

  (:predicates
    (raw ?d - document)             ; document brut, non encore parsé
    (extracted ?d - document)       ; triplets extraits vers le blackboard (ETL)
    (validated ?d - document)       ; conforme aux shapes SHACL
    (enriched ?d - document)        ; clôture OWL-RL matérialisée
    (revalidated ?d - document)     ; re-validation après enrichissement
    (needs-linking ?d - document)   ; doit être synchronisé avec le Linked Data
    (link-satisfied ?d - document)  ; liage effectué (ou non requis)
    (indexed ?d - document)         ; partitionné et indexé via SPARQL
    (failed ?d - document)          ; échec (parsing, violation, inconsistance)
    (processed ?d - document))      ; état final : publié ou mis en quarantaine

  ;; Agent d'extraction (ETL) : parsing multi-format -> graphe nommé
  (:action extract
    :parameters (?d - document)
    :precondition (and (raw ?d) (not (failed ?d)))
    :effect (and (extracted ?d) (not (raw ?d))))

  ;; Agent de validation SHACL
  (:action validate
    :parameters (?d - document)
    :precondition (and (extracted ?d) (not (failed ?d)))
    :effect (validated ?d))

  ;; Agent de raisonnement OWL-RL : enrichissement par inférence
  (:action reason
    :parameters (?d - document)
    :precondition (and (validated ?d) (not (failed ?d)))
    :effect (enriched ?d))

  ;; Re-validation SHACL du graphe enrichi (les inférences peuvent violer)
  (:action revalidate
    :parameters (?d - document)
    :precondition (and (enriched ?d) (not (failed ?d)))
    :effect (revalidated ?d))

  ;; Agent de synchronisation Linked Data (owl:sameAs vers DBpedia/Wikidata)
  (:action link
    :parameters (?d - document)
    :precondition (and (revalidated ?d) (needs-linking ?d) (not (failed ?d)))
    :effect (link-satisfied ?d))

  ;; Agent de requêtage SPARQL : partitionnement + indexation
  (:action index
    :parameters (?d - document)
    :precondition (and (revalidated ?d) (not (failed ?d)))
    :effect (indexed ?d))

  ;; Publication du document dans le graphe de connaissances global
  (:action publish
    :parameters (?d - document)
    :precondition (and (indexed ?d) (link-satisfied ?d) (not (failed ?d)))
    :effect (processed ?d))

  ;; Mise en quarantaine d'un document en échec
  (:action quarantine
    :parameters (?d - document)
    :precondition (failed ?d)
    :effect (processed ?d))
)
