"""Agent orchestrateur : planification PDDL, supervision et replanification.

Pour chaque document, l'orchestrateur :

1. construit un problème PDDL à partir des paramètres d'entrée (statut initial
   ``raw`` et besoin de liage ``needs-linking``/``link-satisfied``), avec pour
   but ``(processed doc)`` ;
2. calcule un plan optimal avec le planificateur STRIPS (``planner.py``) ;
3. exécute le plan en dispatchant chaque action à l'agent spécialisé qui la
   déclare dans ``handles`` ;
4. **supervise** l'issue réelle : si l'agent émet un évènement d'échec
   (``ViolationDetected``, ``ExtractionFailed``, ``InconsistencyDetected``), il
   corrige l'état du monde — ajout du fait ``(failed doc)`` — puis
   **replanifie** ; le nouveau plan emprunte alors la route de quarantaine.

Ce couplage plan/supervision/replanification est la traduction opérationnelle
du paradigme *sense–plan–act* des systèmes multi-agents symboliques.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, List, Optional

from .blackboard import Blackboard
from .events import (DOCUMENT_INGESTED, DOCUMENT_PUBLISHED, DOCUMENT_QUARANTINED,
                     EXTRACTION_FAILED, INCONSISTENCY_DETECTED, VIOLATION_DETECTED,
                     SemanticEvent)
from .planner import Domain, Problem, plan as compute_plan
from .agents.base import Agent

#: évènements qui invalident le plan courant et déclenchent la replanification
_FAILURE_EVENTS = {EXTRACTION_FAILED, VIOLATION_DETECTED, INCONSISTENCY_DETECTED}


class Orchestrator(Agent):
    name = "OrchestratorAgent"

    def __init__(self, blackboard: Blackboard, domain_path: Path,
                 agents: List[Agent]) -> None:
        super().__init__(blackboard)
        self.domain = Domain.parse(domain_path)
        self.dispatch: Dict[str, Agent] = {}
        for agent in agents:
            for act in agent.handles:
                self.dispatch[act] = agent
        self.trace: List[dict] = []

    # ------------------------------------------------------------------ état
    def _initial_state(self, doc: str, needs_linking: bool) -> set:
        state = {("raw", doc)}
        if needs_linking:
            state.add(("needs-linking", doc))
        else:
            state.add(("link-satisfied", doc))
        return state

    def _make_problem(self, doc: str, state: set) -> Problem:
        return Problem.build(objects={doc: "document"},
                             init=state, goal=[("processed", doc)])

    # ------------------------------------------------------------- traitement
    def process_document(self, path: Path, doc_id: Optional[str] = None,
                         needs_linking: bool = False) -> dict:
        """Boucle plan → exécution → supervision → replanification."""
        path = Path(path)
        doc_id = doc_id or path.stem
        doc_uri = self.blackboard.register_document(doc_id, path)
        self.emit(DOCUMENT_INGESTED, doc_uri, file=path.name,
                  needsLinking=needs_linking)

        state = self._initial_state(doc_id, needs_linking)
        executed: List[str] = []
        replans = 0
        started = time.perf_counter()

        while True:
            steps = compute_plan(self.domain, self._make_problem(doc_id, state))
            if steps is None:
                raise RuntimeError(f"Aucun plan trouvé pour {doc_id} depuis {state}")
            if not steps:
                break  # but atteint

            failed = False
            for step in steps:
                if step.name == "quarantine":
                    self.blackboard.documents[doc_uri]["status"] = "quarantined"
                    self.emit(DOCUMENT_QUARANTINED, doc_uri,
                              afterActions=", ".join(executed))
                    outcome: Optional[SemanticEvent] = None
                elif step.name == "publish":
                    self.blackboard.documents[doc_uri]["status"] = "published"
                    self.emit(DOCUMENT_PUBLISHED, doc_uri,
                              pipeline=", ".join(executed))
                    outcome = None
                else:
                    agent = self.dispatch[step.name]
                    outcome = agent.perform(step.name, doc_uri)
                executed.append(step.signature)

                if outcome is not None and outcome.type in _FAILURE_EVENTS:
                    # L'issue contredit l'effet attendu -> correction de l'état
                    # du monde et replanification (route de quarantaine).
                    state.add(("failed", doc_id))
                    replans += 1
                    failed = True
                    break
                state = step.apply(frozenset(state))
                state = set(state)

            if failed:
                continue
            break

        elapsed = time.perf_counter() - started
        record = {
            "doc_uri": doc_uri,
            "doc_id": doc_id,
            "status": self.blackboard.documents[doc_uri]["status"],
            "plan": executed,
            "replans": replans,
            "seconds": elapsed,
            "triples": self.blackboard.documents[doc_uri].get("triples", 0),
            "inferred": self.blackboard.documents[doc_uri].get("inferred", 0),
        }
        self.trace.append(record)
        return record

    def process_corpus(self, docs: List[dict]) -> List[dict]:
        return [self.process_document(Path(d["path"]),
                                      doc_id=d.get("id"),
                                      needs_linking=d.get("needs_linking", False))
                for d in docs]
