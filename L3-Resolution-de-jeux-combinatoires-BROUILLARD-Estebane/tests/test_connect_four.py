"""Tests du moteur de jeu Puissance 4.

Couvre : coups légaux/illégaux, gravité, les quatre directions de victoire
(horizontale, verticale, deux diagonales), match nul, et les propriétés du
hash de Zobrist (incrémental, réversible, cohérent).
"""

import pytest

from game.connect_four import (
    COLS,
    EMPTY,
    PLAYER1,
    PLAYER2,
    ROWS,
    ConnectFour,
)


def play_sequence(game: ConnectFour, cols):
    """Joue une suite de colonnes en alternant automatiquement les joueurs."""
    for c in cols:
        game.play_move(c)


# --------------------------------------------------------------------------- #
# Coups, gravité, légalité
# --------------------------------------------------------------------------- #
def test_initial_state():
    g = ConnectFour()
    assert g.current_player == PLAYER1
    assert g.legal_moves() == list(range(COLS))
    assert g.zobrist_hash == 0
    assert not g.is_terminal()


def test_gravity_stacks_in_column():
    g = ConnectFour()
    g.play_move(3)  # joueur 1 en bas de la colonne 3
    g.play_move(3)  # joueur 2 au-dessus
    assert g.board[0][3] == PLAYER1
    assert g.board[1][3] == PLAYER2
    assert g.heights[3] == 2


def test_player_alternation():
    g = ConnectFour()
    assert g.current_player == PLAYER1
    g.play_move(0)
    assert g.current_player == PLAYER2
    g.play_move(1)
    assert g.current_player == PLAYER1


def test_illegal_move_out_of_range():
    g = ConnectFour()
    with pytest.raises(ValueError):
        g.play_move(COLS)  # colonne inexistante


def test_illegal_move_full_column():
    g = ConnectFour()
    for _ in range(ROWS):
        g.play_move(2)
    assert 2 not in g.legal_moves()
    with pytest.raises(ValueError):
        g.play_move(2)


# --------------------------------------------------------------------------- #
# Conditions de victoire : les quatre directions
# --------------------------------------------------------------------------- #
def test_horizontal_win():
    g = ConnectFour()
    # J1 joue colonnes 0,1,2,3 ; J2 répond plus haut sur les mêmes colonnes.
    play_sequence(g, [0, 0, 1, 1, 2, 2, 3])
    assert g.winner() == PLAYER1
    assert g.is_terminal()


def test_vertical_win():
    g = ConnectFour()
    # J1 empile 4 jetons colonne 4 ; J2 joue ailleurs.
    play_sequence(g, [4, 0, 4, 1, 4, 2, 4])
    assert g.winner() == PLAYER1


def test_diagonal_up_win():
    g = ConnectFour()
    # Construit une diagonale montante (/) pour le joueur 1.
    # Cible : (0,0),(1,1),(2,2),(3,3).
    moves = [
        0,  # J1 (0,0)
        1,  # J2 (0,1)
        1,  # J1 (1,1)
        2,  # J2 (0,2)
        2,  # J1 -> (1,2)
        3,  # J2 (0,3)
        2,  # J1 (2,2)
        3,  # J2 (1,3)
        3,  # J1 (2,3)... pas encore
        6,  # J2 ailleurs
        3,  # J1 (3,3) -> complète la diagonale (0,0)(1,1)(2,2)(3,3)
    ]
    play_sequence(g, moves)
    assert g.winner() == PLAYER1


def test_diagonal_down_win():
    g = ConnectFour()
    # Diagonale descendante (\) pour le joueur 1 : (3,0),(2,1),(1,2),(0,3).
    moves = [
        3,  # J1 (0,3)
        2,  # J2 (0,2)
        2,  # J1 (1,2)
        1,  # J2 (0,1)
        1,  # J1 -> (1,1)
        0,  # J2 (0,0)
        1,  # J1 (2,1)
        0,  # J2 (1,0)
        0,  # J1 (2,0)
        6,  # J2 ailleurs
        0,  # J1 (3,0) -> complète (3,0)(2,1)(1,2)(0,3)
    ]
    play_sequence(g, moves)
    assert g.winner() == PLAYER1


def test_no_winner_on_empty_and_partial():
    g = ConnectFour()
    assert g.winner() is None
    play_sequence(g, [0, 1, 0, 1])
    assert g.winner() is None


def test_draw_full_board_no_winner():
    g = ConnectFour()
    # On force directement un plateau plein sans gagnant pour tester is_full/draw.
    g.board = [[EMPTY] * COLS for _ in range(ROWS)]
    fill = [
        [1, 2, 1, 2, 1, 2],
        [1, 2, 1, 2, 1, 2],
        [2, 1, 2, 1, 2, 1],
        [2, 1, 2, 1, 2, 1],
        [1, 2, 1, 2, 1, 2],
        [1, 2, 1, 2, 1, 2],
        [2, 1, 2, 1, 2, 1],
    ]
    for c in range(COLS):
        for r in range(ROWS):
            g.board[r][c] = fill[c][r]
        g.heights[c] = ROWS
    assert g.is_full()
    assert g.winner() is None
    assert g.is_terminal()


# --------------------------------------------------------------------------- #
# Hash de Zobrist
# --------------------------------------------------------------------------- #
def test_zobrist_undo_restores_hash():
    g = ConnectFour()
    h0 = g.zobrist_hash
    g.play_move(3)
    h1 = g.zobrist_hash
    assert h1 != h0
    g.undo_move()
    assert g.zobrist_hash == h0  # le XOR est sa propre inverse


def test_zobrist_path_independence():
    """Deux ordres de coups menant à la MÊME position -> même hash."""
    g1 = ConnectFour()
    play_sequence(g1, [3, 2, 4, 1])
    g2 = ConnectFour()
    play_sequence(g2, [4, 1, 3, 2])  # mêmes jetons posés aux mêmes cases
    # Vérifie que les plateaux sont bien identiques avant de comparer les hashes.
    assert g1.board == g2.board
    assert g1.zobrist_hash == g2.zobrist_hash


def test_zobrist_distinguishes_player():
    """La même case occupée par des joueurs différents donne des hashes différents."""
    g1 = ConnectFour()
    g1.play_move(0)  # J1 en (0,0)
    g2 = ConnectFour()
    g2.play_move(1)  # J2 jouera en (0,0) après un coup de J1 ailleurs
    g2.play_move(0)
    # g2 : (0,1)=J1, (0,0)=J2 ; g1 : (0,0)=J1. Hashes distincts.
    assert g1.zobrist_hash != g2.zobrist_hash


def test_full_undo_returns_to_start():
    g = ConnectFour()
    moves = [3, 3, 2, 4, 1, 0, 5]
    play_sequence(g, moves)
    for _ in moves:
        g.undo_move()
    assert g.zobrist_hash == 0
    assert g.current_player == PLAYER1
    assert all(h == 0 for h in g.heights)
    assert all(cell == EMPTY for row in g.board for cell in row)


def test_copy_is_independent():
    g = ConnectFour()
    play_sequence(g, [3, 2])
    clone = g.copy()
    clone.play_move(3)
    # Modifier la copie ne doit pas changer l'original.
    assert g.heights[3] == 1
    assert clone.heights[3] == 2
    assert g.zobrist_hash != clone.zobrist_hash
