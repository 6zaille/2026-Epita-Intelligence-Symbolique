"""J3 — Serveur MCP d'outils d'analyse symbolique.

Expose des solveurs/raisonneurs symboliques (SAT, SMT, OWL) derriere le
protocole Model Context Protocol (MCP), afin qu'un LLM puisse les orchestrer
comme des outils. Le serveur reste totalement agnostique du LLM : n'importe
quel hote MCP (l'hote Gemini fourni dans `host/`, MCP Inspector...) peut s'y
connecter.
"""

__version__ = "0.1.0"
