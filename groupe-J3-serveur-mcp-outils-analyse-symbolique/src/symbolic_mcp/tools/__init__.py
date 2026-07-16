"""Outils symboliques exposes par le serveur MCP.

Chaque module fournit une fonction *pure* (sans dependance MCP) qui prend des
arguments JSON-serialisables et renvoie un dict JSON-serialisable. Cela permet
de les tester unitairement et de les enregistrer ensuite comme outils MCP dans
`symbolic_mcp.server`.
"""

from .sat_tool import solve_sat
from .smt_tool import solve_smt
from .owl_tool import owl_reason

__all__ = ["solve_sat", "solve_smt", "owl_reason"]
