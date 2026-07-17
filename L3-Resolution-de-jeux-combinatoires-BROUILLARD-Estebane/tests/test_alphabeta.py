"""Tests de l'agent alpha-beta (étape 3).

Deux familles de tests :
1. CORRECTION tactique : l'agent gagne quand il peut, et bloque l'adversaire.
2. INVARIANT d'ablation : minimax pur, +αβ, +TT, +move ordering doivent tous
   renvoyer la MÊME valeur racine (les optimisations ne changent que le nombre
   de nœuds explorés, pas le résultat — c'est l'argument de Knuth & Moore).
   Et l'élagage/TT/ordering doivent réduire (ou égaler) le nombre de nœuds.
"""

import pytest

from agents.alphabeta import AlphaBetaAgent, evaluate
from game.connect_four import PLAYER1, PLAYER2, ConnectFour


def make_game(moves):
    g = ConnectFour()
    for c in moves:
        g.play_move(c)
    return g


# --------------------------------------------------------------------------- #
# Correction tactique
# --------------------------------------------------------------------------- #
def test_takes_immediate_winning_move():
    # J1 a trois jetons alignés colonne 0,1,2 (en bas) ; le coup gagnant est col 3.
    # Séquence : J1=0, J2=0(haut), J1=1, J2=1, J1=2, J2=2 -> J1 au trait, joue 3 = win.
    g = make_game([0, 0, 1, 1, 2, 2])
    assert g.current_player == PLAYER1
    agent = AlphaBetaAgent(depth=4)
    assert agent.move(g) == 3


def test_blocks_opponent_immediate_win():
    # J2 menace de gagner et J1 n'a AUCUN coup gagnant : il doit donc bloquer.
    # J2 aligne (0,1),(0,2),(0,3). (0,0) est occupé par J1 -> seule menace : col 4.
    # J1 a (0,0),(0,5),(0,6) : aucun alignement de 3, donc pas de victoire immédiate.
    g = make_game([0, 1, 5, 2, 6, 3])
    assert g.current_player == PLAYER1
    # Tout coup autre que 4 laisse J2 compléter en col 4 -> J1 doit jouer 4.
    agent = AlphaBetaAgent(depth=4)
    assert agent.move(g) == 4


def test_evaluate_symmetry_empty_board():
    g = ConnectFour()
    # Plateau vide : évaluation symétrique -> 0 pour les deux joueurs.
    assert evaluate(g, PLAYER1) == 0
    assert evaluate(g, PLAYER2) == 0


def test_evaluate_center_preference():
    g = ConnectFour()
    g.play_move(3)  # J1 au centre
    # La position doit être (faiblement) favorable à J1 grâce au contrôle du centre.
    assert evaluate(g, PLAYER1) > 0
    assert evaluate(g, PLAYER2) < 0


# --------------------------------------------------------------------------- #
# Invariant d'ablation : même valeur, moins de nœuds
# --------------------------------------------------------------------------- #
# Quelques positions de test à profondeur fixe.
POSITIONS = [
    [],                      # plateau vide
    [3],                     # un coup au centre
    [3, 3, 4, 2],            # début de partie
    [3, 2, 3, 4, 5, 1],      # milieu de partie
]


@pytest.mark.parametrize("moves", POSITIONS)
def test_ablation_same_root_value(moves):
    """Toutes les configurations renvoient la même valeur racine."""
    g = make_game(moves)
    depth = 4

    configs = {
        "minimax": dict(use_alpha_beta=False, use_transposition=False, use_move_ordering=False),
        "ab": dict(use_alpha_beta=True, use_transposition=False, use_move_ordering=False),
        "ab_tt": dict(use_alpha_beta=True, use_transposition=True, use_move_ordering=False),
        "ab_tt_order": dict(use_alpha_beta=True, use_transposition=True, use_move_ordering=True),
    }

    values = {}
    for label, cfg in configs.items():
        agent = AlphaBetaAgent(depth=depth, **cfg)
        agent.reset()
        _, value, _ = agent.search(g)
        values[label] = value

    ref = values["minimax"]
    for label, v in values.items():
        assert v == ref, f"{label}={v} != minimax={ref} pour moves={moves}"


@pytest.mark.parametrize("moves", POSITIONS)
def test_pruning_reduces_nodes(moves):
    """L'élagage αβ explore au plus autant de nœuds que minimax pur."""
    g = make_game(moves)
    depth = 4

    minimax = AlphaBetaAgent(depth=depth, use_alpha_beta=False, use_transposition=False, use_move_ordering=False)
    minimax.reset(); minimax.search(g)

    ab = AlphaBetaAgent(depth=depth, use_alpha_beta=True, use_transposition=False, use_move_ordering=False)
    ab.reset(); ab.search(g)

    ab_order = AlphaBetaAgent(depth=depth, use_alpha_beta=True, use_transposition=False, use_move_ordering=True)
    ab_order.reset(); ab_order.search(g)

    # αβ ne peut qu'explorer moins de nœuds que minimax exhaustif.
    assert ab.nodes <= minimax.nodes
    # Avec un bon move ordering, αβ explore généralement encore moins de nœuds.
    assert ab_order.nodes <= minimax.nodes


def test_move_ordering_helps_on_nonempty_position():
    """Sur une vraie position, le move ordering réduit le nombre de nœuds."""
    g = make_game([3, 2, 3, 4, 5, 1])
    depth = 5
    ab = AlphaBetaAgent(depth=depth, use_alpha_beta=True, use_transposition=False, use_move_ordering=False)
    ab.reset(); ab.search(g)
    ab_order = AlphaBetaAgent(depth=depth, use_alpha_beta=True, use_transposition=False, use_move_ordering=True)
    ab_order.reset(); ab_order.search(g)
    assert ab_order.nodes < ab.nodes


def test_tree_recording_marks_pruned_branches():
    """L'enregistrement de l'arbre marque bien des branches élaguées."""
    g = make_game([3, 2, 3, 4])
    agent = AlphaBetaAgent(depth=4, use_alpha_beta=True, use_move_ordering=True)
    agent.reset()
    agent.search(g, record_tree=True)
    tree = agent.last_tree
    assert tree is not None

    # Parcours : il doit exister au moins une branche élaguée dans l'arbre.
    def has_pruned(node):
        if node.pruned:
            return True
        return any(has_pruned(c) for c in node.children)

    assert has_pruned(tree)
