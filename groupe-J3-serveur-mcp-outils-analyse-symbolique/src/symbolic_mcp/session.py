"""Gestion des sessions et du contexte du serveur MCP.

Le sujet J3 demande de "gerer les sessions, le contexte et la traduction
bidirectionnelle entre LLM et outils symboliques". Ce module fournit un
gestionnaire de sessions en memoire :

- chaque session possede un identifiant, un journal d'appels d'outils
  (tracabilite de la chaine LLM -> outil), et un magasin d'artefacts nommes
  (ex. reutiliser une CNF ou une ontologie d'un appel a l'autre) ;
- le journal constitue le "contexte" que le LLM peut relire pour enchainer
  ses raisonnements.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Session:
    id: str
    created_at: float = field(default_factory=time.time)
    history: list[dict[str, Any]] = field(default_factory=list)
    store: dict[str, Any] = field(default_factory=dict)

    def log(self, tool: str, arguments_summary: str, result_summary: str) -> None:
        self.history.append(
            {
                "step": len(self.history) + 1,
                "tool": tool,
                "arguments": arguments_summary,
                "result": result_summary,
                "at": time.time(),
            }
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "session_id": self.id,
            "created_at": self.created_at,
            "n_calls": len(self.history),
            "history": self.history,
            "stored_artifacts": sorted(self.store.keys()),
        }


class SessionManager:
    """Cree et retrouve des sessions de maniere thread-safe."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def create(self) -> Session:
        with self._lock:
            sid = uuid.uuid4().hex[:12]
            session = Session(id=sid)
            self._sessions[sid] = session
            return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            return self._sessions.get(session_id)

    def get_or_create(self, session_id: str | None) -> Session:
        if session_id:
            existing = self.get(session_id)
            if existing is not None:
                return existing
        return self.create()

    def list_ids(self) -> list[str]:
        with self._lock:
            return list(self._sessions.keys())
