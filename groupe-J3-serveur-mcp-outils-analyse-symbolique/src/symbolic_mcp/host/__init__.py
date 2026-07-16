"""Hotes LLM pour le serveur MCP d'analyse symbolique.

Le serveur MCP est agnostique du LLM. Ce sous-paquet fournit un *hote* de
reference base sur Gemini (`gemini_host`) qui : se connecte au serveur MCP,
expose ses outils a Gemini, laisse le LLM orchestrer les appels, et trace la
chaine LLM -> outil symbolique (support de l'evaluation).
"""

from .gemini_host import GeminiMCPHost

__all__ = ["GeminiMCPHost"]
