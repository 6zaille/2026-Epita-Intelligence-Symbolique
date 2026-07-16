"""Plateau de Puissance 4 (Connect Four).

Plateau 6 lignes x 7 colonnes. Deux joueurs : 1 et 2 (le vide est 0).
Le joueur 1 commence par convention.

Conventions importantes :
- L'indice de ligne 0 est la ligne du BAS du plateau (gravité : les jetons tombent).
  Cela simplifie le calcul de la prochaine case libre d'une colonne.
- Un coup est l'indice de colonne (0..6) dans lequel on lâche un jeton.
- Le hash de Zobrist permet d'indexer les tables de transposition des agents :
  chaque (case, joueur) reçoit un nombre aléatoire 64 bits ; le hash d'une position
  est le XOR des nombres des cases occupées. Mettre/enlever un jeton = un seul XOR,
  donc le hash se met à jour de façon incrémentale et réversible.

Référence : tables de transposition — voir Knuth & Moore (1975) pour le lien avec
l'élagage alpha-beta.
"""

from __future__ import annotations

import random
from typing import List, Optional, Tuple

# Dimensions standard du Puissance 4.
ROWS = 6
COLS = 7
# Nombre de jetons alignés nécessaires pour gagner.
CONNECT = 4

# Les deux joueurs et le symbole de case vide.
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2


def _init_zobrist(seed: int = 20240601) -> List[List[List[int]]]:
    """Construit la table de nombres aléatoires de Zobrist.

    Indexée par [ligne][colonne][joueur-1]. On utilise un générateur dédié avec
    une graine fixe pour que les hashes soient reproductibles d'une exécution à
    l'autre (utile pour les tests et la comparaison des agents).
    """
    rng = random.Random(seed)
    table = [
        [[rng.getrandbits(64) for _ in range(2)] for _ in range(COLS)]
        for _ in range(ROWS)
    ]
    return table


# Table partagée par toutes les positions : doit rester constante pendant un run.
_ZOBRIST = _init_zobrist()


class ConnectFour:
    """État mutable d'une partie de Puissance 4.

    Le plateau est stocké comme une liste de listes d'entiers (ROWS x COLS).
    On maintient en parallèle :
    - `heights[c]` : nombre de jetons déjà dans la colonne c (= indice de la
      prochaine case libre), pour jouer/annuler un coup en O(1).
    - `zobrist_hash` : hash de Zobrist de la position courante, mis à jour
      incrémentalement à chaque coup.
    - `move_history` : pile des colonnes jouées, pour `undo_move`.
    """

    __slots__ = ("board", "heights", "current_player", "zobrist_hash", "move_history")

    def __init__(self) -> None:
        self.board: List[List[int]] = [[EMPTY] * COLS for _ in range(ROWS)]
        self.heights: List[int] = [0] * COLS
        self.current_player: int = PLAYER1
        self.zobrist_hash: int = 0
        self.move_history: List[int] = []

    # ------------------------------------------------------------------ #
    # Coups
    # ------------------------------------------------------------------ #
    def legal_moves(self) -> List[int]:
        """Liste des colonnes jouables (celles qui ne sont pas pleines)."""
        return [c for c in range(COLS) if self.heights[c] < ROWS]

    def is_legal(self, col: int) -> bool:
        """Vrai si la colonne `col` existe et n'est pas pleine."""
        return 0 <= col < COLS and self.heights[col] < ROWS

    def play_move(self, col: int) -> None:
        """Joue un jeton du joueur courant dans la colonne `col`.

        Met à jour le plateau, la hauteur de colonne, le hash de Zobrist puis
        passe la main à l'autre joueur. Lève ValueError si le coup est illégal.
        """
        if not self.is_legal(col):
            raise ValueError(f"Coup illégal : colonne {col} (hauteurs={self.heights})")
        row = self.heights[col]
        player = self.current_player
        self.board[row][col] = player
        self.heights[col] += 1
        # XOR du nombre de Zobrist associé à (case, joueur) : pose du jeton.
        self.zobrist_hash ^= _ZOBRIST[row][col][player - 1]
        self.move_history.append(col)
        self.current_player = PLAYER2 if player == PLAYER1 else PLAYER1

    def undo_move(self) -> None:
        """Annule le dernier coup joué (opération inverse exacte de play_move)."""
        if not self.move_history:
            raise ValueError("Aucun coup à annuler.")
        col = self.move_history.pop()
        self.heights[col] -= 1
        row = self.heights[col]
        # Le joueur qui avait joué ce coup est l'adversaire du joueur courant.
        player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1
        self.board[row][col] = EMPTY
        # Même XOR : l'opération est sa propre inverse, le hash redevient l'ancien.
        self.zobrist_hash ^= _ZOBRIST[row][col][player - 1]
        self.current_player = player

    # ------------------------------------------------------------------ #
    # Fin de partie
    # ------------------------------------------------------------------ #
    def winner(self) -> Optional[int]:
        """Renvoie le joueur gagnant (1 ou 2) s'il y a un alignement, sinon None.

        Parcourt les quatre directions (horizontale, verticale, deux diagonales).
        Pour la performance des agents on pourrait ne tester qu'autour du dernier
        coup ; ici on garde une version claire et complète, suffisante pour le jeu.
        """
        b = self.board
        for r in range(ROWS):
            for c in range(COLS):
                p = b[r][c]
                if p == EMPTY:
                    continue
                # Horizontale (vers la droite).
                if c + CONNECT <= COLS and all(b[r][c + k] == p for k in range(CONNECT)):
                    return p
                # Verticale (vers le haut).
                if r + CONNECT <= ROWS and all(b[r + k][c] == p for k in range(CONNECT)):
                    return p
                # Diagonale montante (/).
                if (
                    r + CONNECT <= ROWS
                    and c + CONNECT <= COLS
                    and all(b[r + k][c + k] == p for k in range(CONNECT))
                ):
                    return p
                # Diagonale descendante (\).
                if (
                    r - CONNECT + 1 >= 0
                    and c + CONNECT <= COLS
                    and all(b[r - k][c + k] == p for k in range(CONNECT))
                ):
                    return p
        return None

    def is_full(self) -> bool:
        """Vrai si toutes les colonnes sont pleines (match nul si pas de gagnant)."""
        return all(h >= ROWS for h in self.heights)

    def is_terminal(self) -> bool:
        """Vrai si la partie est finie : victoire d'un joueur ou plateau plein."""
        return self.winner() is not None or self.is_full()

    # ------------------------------------------------------------------ #
    # Utilitaires
    # ------------------------------------------------------------------ #
    def copy(self) -> "ConnectFour":
        """Copie profonde et indépendante de l'état (utile pour MCTS/simulations)."""
        clone = ConnectFour.__new__(ConnectFour)
        clone.board = [row[:] for row in self.board]
        clone.heights = self.heights[:]
        clone.current_player = self.current_player
        clone.zobrist_hash = self.zobrist_hash
        clone.move_history = self.move_history[:]
        return clone

    def render(self) -> str:
        """Représentation texte du plateau (ligne du haut en premier)."""
        symbols = {EMPTY: ".", PLAYER1: "X", PLAYER2: "O"}
        lines = []
        for r in range(ROWS - 1, -1, -1):  # du haut vers le bas pour l'affichage
            lines.append(" ".join(symbols[self.board[r][c]] for c in range(COLS)))
        lines.append(" ".join(str(c) for c in range(COLS)))  # numéros de colonnes
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.render()


def zobrist_table() -> List[List[List[int]]]:
    """Accès en lecture à la table de Zobrist (pour tests/inspection)."""
    return _ZOBRIST
