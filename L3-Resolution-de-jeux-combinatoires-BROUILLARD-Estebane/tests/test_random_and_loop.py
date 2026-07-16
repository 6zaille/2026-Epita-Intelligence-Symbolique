"""Tests de l'agent aléatoire et de la boucle de jeu (étape 2).

Vérifie que : l'agent aléatoire ne joue que des coups légaux et est reproductible
à graine fixe, que la boucle de jeu se termine toujours, et que le round-robin
produit des décomptes cohérents.
"""

from agents.random_agent import RandomAgent
from game.connect_four import ConnectFour
from tournament.runner import play_game, play_match, round_robin


def test_random_agent_plays_only_legal_moves():
    agent = RandomAgent(seed=0)
    game = ConnectFour()
    for _ in range(20):
        if game.is_terminal():
            break
        col = agent.move(game)
        assert col in game.legal_moves()
        game.play_move(col)


def test_random_agent_is_reproducible_with_seed():
    g1 = play_game(RandomAgent(seed=42), RandomAgent(seed=7))
    g2 = play_game(RandomAgent(seed=42), RandomAgent(seed=7))
    assert g1.moves == g2.moves
    assert g1.winner == g2.winner


def test_game_loop_terminates():
    res = play_game(RandomAgent(seed=1), RandomAgent(seed=2))
    # Une partie de Puissance 4 a au plus 42 coups.
    assert len(res.moves) <= 42
    # Soit quelqu'un gagne, soit le plateau est plein (nul) -> winner peut être None.
    assert res.winner in (None, 1, 2)
    # Autant de temps mesurés que de coups joués.
    assert len(res.move_times) == len(res.moves)


def test_play_match_counts_sum_to_n_games():
    n = 10
    out = play_match(RandomAgent(seed=3), RandomAgent(seed=4), n_games=n)
    assert out["wins_a"] + out["wins_b"] + out["draws"] == n


def test_round_robin_covers_all_pairs():
    agents = [RandomAgent(seed=i) for i in range(3)]
    for i, a in enumerate(agents):
        a.name = f"R{i}"
    results = round_robin(agents, n_games=4, verbose=False)
    # 3 agents -> C(3,2) = 3 paires.
    assert len(results) == 3
    pairs = {(a, b) for a, b, _ in results}
    assert ("R0", "R1") in pairs
    assert ("R0", "R2") in pairs
    assert ("R1", "R2") in pairs
