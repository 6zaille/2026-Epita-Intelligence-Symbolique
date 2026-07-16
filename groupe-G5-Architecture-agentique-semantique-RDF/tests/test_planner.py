"""Tests du planificateur PDDL (parsing, grounding, recherche, replanification)."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from rdf_agents.planner import Domain, Problem, plan

DOMAIN = Domain.parse(ROOT / "planning/domain.pddl")


def _names(steps):
    return [s.name for s in steps]


def test_domain_parsing():
    assert DOMAIN.name == "rdf-pipeline"
    names = {a.name for a in DOMAIN.actions}
    assert names == {"extract", "validate", "reason", "revalidate",
                     "link", "index", "publish", "quarantine"}
    extract = next(a for a in DOMAIN.actions if a.name == "extract")
    assert ("raw", "?d") in extract.positive_pre
    assert ("failed", "?d") in extract.negative_pre       # précondition négative
    assert ("raw", "?d") in extract.del_effects           # effet delete


def test_nominal_plan_without_linking():
    problem = Problem.build(
        objects={"d": "document"},
        init=[("raw", "d"), ("link-satisfied", "d")],
        goal=[("processed", "d")])
    steps = plan(DOMAIN, problem)
    assert _names(steps) == ["extract", "validate", "reason",
                             "revalidate", "index", "publish"]


def test_nominal_plan_with_linking():
    problem = Problem.build(
        objects={"d": "document"},
        init=[("raw", "d"), ("needs-linking", "d")],
        goal=[("processed", "d")])
    steps = plan(DOMAIN, problem)
    assert "link" in _names(steps)
    assert _names(steps).index("link") < _names(steps).index("publish")


def test_replanning_after_failure_routes_to_quarantine():
    # État corrigé par l'orchestrateur après un ViolationDetected
    problem = Problem.build(
        objects={"d": "document"},
        init=[("extracted", "d"), ("failed", "d"), ("link-satisfied", "d")],
        goal=[("processed", "d")])
    steps = plan(DOMAIN, problem)
    assert _names(steps) == ["quarantine"]


def test_failed_document_cannot_be_published():
    # Aucune action nominale n'est applicable si (failed d) : seul quarantine mène au but
    problem = Problem.build(
        objects={"d": "document"},
        init=[("indexed", "d"), ("link-satisfied", "d"), ("failed", "d")],
        goal=[("processed", "d")])
    steps = plan(DOMAIN, problem)
    assert _names(steps) == ["quarantine"]


def test_plans_are_optimal_bfs():
    problem = Problem.build(
        objects={"d": "document"},
        init=[("raw", "d"), ("link-satisfied", "d")],
        goal=[("processed", "d")])
    steps = plan(DOMAIN, problem)
    # BFS => plan optimal : la séquence nominale complète, sans détour ni action
    # superflue (comparaison exacte, pas seulement la longueur).
    assert _names(steps) == ["extract", "validate", "reason",
                             "revalidate", "index", "publish"]
    assert len(steps) == 6
    # Borne inférieure : un état déjà à un pas du but n'engendre qu'une action.
    # Un planificateur sous-optimal qui rallongerait le plan échouerait ici.
    near = Problem.build(
        objects={"d": "document"},
        init=[("indexed", "d"), ("link-satisfied", "d")],
        goal=[("processed", "d")])
    assert _names(plan(DOMAIN, near)) == ["publish"]


def test_multi_document_grounding():
    problem = Problem.build(
        objects={"a": "document", "b": "document"},
        init=[("raw", "a"), ("link-satisfied", "a"),
              ("raw", "b"), ("link-satisfied", "b")],
        goal=[("processed", "a"), ("processed", "b")])
    steps = plan(DOMAIN, problem)
    assert steps is not None
    # 6 actions nominales par document, aucune mutualisation entre documents
    assert len(steps) == 12
    assert {args for s in steps for args in s.args} == {"a", "b"}
    # chaque document parcourt réellement sa propre séquence nominale jusqu'à publish
    nominal = ["extract", "validate", "reason", "revalidate", "index", "publish"]
    assert [s.name for s in steps if s.args == ("a",)] == nominal
    assert [s.name for s in steps if s.args == ("b",)] == nominal
