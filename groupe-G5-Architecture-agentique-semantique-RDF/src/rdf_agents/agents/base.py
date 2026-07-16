"""Classe de base des agents spécialisés.

Chaque agent est un module autonome qui :
1. lit ses entrées dans le graphe de connaissances partagé (blackboard) ;
2. exécute une opération spécialisée sur les documents RDF ;
3. écrit ses sorties (graphes enrichis/validés, rapports) dans le blackboard ;
4. rend compte via des évènements sémantiques publiés sur le bus.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from ..blackboard import Blackboard
from ..events import SemanticEvent


class Agent:
    """Agent autonome opérant sur le graphe de connaissances partagé."""

    name = "Agent"
    #: nom de l'action PDDL que cet agent sait exécuter
    handles: tuple = ()

    def __init__(self, blackboard: Blackboard) -> None:
        self.blackboard = blackboard
        self.bus = blackboard.bus
        self.timings: list = []

    def emit(self, event_type: str, doc_uri: str, **payload: Any) -> SemanticEvent:
        event = SemanticEvent(type=event_type, emitter=self.name,
                              document=doc_uri, payload=payload)
        return self.bus.publish(event)

    def perform(self, action: str, doc_uri: str) -> SemanticEvent:
        """Point d'entrée appelé par l'orchestrateur pour une action du plan."""
        start = time.perf_counter()
        try:
            event = self._execute(action, doc_uri)
        finally:
            self.timings.append((action, doc_uri, time.perf_counter() - start))
        return event

    def _execute(self, action: str, doc_uri: str) -> SemanticEvent:  # pragma: no cover
        raise NotImplementedError
