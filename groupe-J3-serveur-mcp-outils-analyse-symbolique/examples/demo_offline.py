"""Demo hors-ligne des trois outils symboliques (aucune clef LLM requise).

Illustre, pour chaque outil, la chaine : probleme en langage naturel -> mise en
forme symbolique -> appel de l'outil -> conclusion en langage naturel. C'est la
meme sequence qu'un LLM realiserait via MCP, mais ecrite a la main pour une
demonstration reproductible et sans dependance reseau.

    python examples/demo_offline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from symbolic_mcp.tools import owl_reason, solve_sat, solve_smt  # noqa: E402


def section(title: str) -> None:
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


def demo_sat() -> None:
    section("SAT — enigme logique booleenne")
    print(
        "Probleme : 'S'il pleut, je prends un parapluie. Il pleut. "
        "Or je n'ai pas de parapluie.' Est-ce coherent ?"
    )
    # pluie=1, parapluie=2 :  (pluie -> parapluie) = (-1 v 2) ; pluie ; -parapluie
    clauses = [[-1, 2], [1], [-2]]
    print(f"Formalisation CNF (DIMACS) : {clauses}")
    r = solve_sat(clauses, var_names={"1": "pluie", "2": "parapluie"})
    print(f"Resultat outil : {r['status']}")
    print(f"Conclusion : {r['summary']}")


def demo_smt() -> None:
    section("SMT — probleme arithmetique sur les entiers")
    print("Probleme : 'Anne a le double de l'age de Bob ; dans 5 ans la somme "
          "de leurs ages sera 40. Quels ages ?'")
    smt = (
        "(declare-const anne Int)\n"
        "(declare-const bob Int)\n"
        "(assert (= anne (* 2 bob)))\n"
        "(assert (= (+ (+ anne 5) (+ bob 5)) 40))\n"
        "(assert (> bob 0))"
    )
    print("Formalisation SMT-LIB2 :\n" + smt)
    r = solve_smt(smt)
    print(f"Resultat outil : {r['status']}  modele={r.get('model')}")
    print(f"Conclusion : {r['summary']}")


def demo_owl() -> None:
    section("OWL — coherence et subsomption ontologique")
    print("Probleme : 'Tout chien est un mammifere, tout mammifere un animal. "
          "Rex est un chien. Rex est-il un animal ?'")
    ttl = (
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix : <http://ex.org/zoo#> .\n"
        ":Animal a owl:Class .\n"
        ":Mammal a owl:Class ; rdfs:subClassOf :Animal .\n"
        ":Dog a owl:Class ; rdfs:subClassOf :Mammal .\n"
        ":rex a :Dog ."
    )
    print("Formalisation OWL (Turtle) :\n" + ttl)
    r = owl_reason(ttl, fmt="turtle", operation="classify")
    print(f"Resultat outil : coherente={r['consistent']} ; "
          f"types inferes de rex = {r['individual_types'].get('rex')}")
    print(f"Conclusion : Rex est bien un animal (inference du reasoner). {r['summary']}")


if __name__ == "__main__":
    demo_sat()
    demo_smt()
    demo_owl()
    print("\n" + "-" * 70)
    print("Ces memes outils sont exposes via MCP et orchestres par un LLM :")
    print("  python -m symbolic_mcp.host.gemini_host --prompt \"...\"")
