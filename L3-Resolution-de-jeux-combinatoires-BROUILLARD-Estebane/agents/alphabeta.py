"""Joueur minimax avec élagage alpha-beta, table de transposition, move ordering.

Construit de façon incrémentale et CONFIGURABLE : chaque optimisation peut être
activée/désactivée indépendamment via le constructeur. C'est volontaire : la
visualisation clé du projet (Knuth & Moore 1975) compare le nombre de nœuds
explorés selon les variantes :

    minimax pur  →  + alpha-beta  →  + table de transposition  →  + move ordering

L'agent expose donc des COMPTEURS (`nodes`, `tt_hits`, `cutoffs`) remis à zéro à
chaque recherche, et peut enregistrer l'arbre de recherche (branches coupées
comprises) pour le dessiner.

Formulation : negamax (minimax symétrique). Le score est toujours évalué du point
de vue du joueur dont c'est le tour. Un score positif = position favorable au
joueur au trait.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from agents.base import Agent
from game.connect_four import COLS, EMPTY, PLAYER1, PLAYER2, ROWS, ConnectFour

# Valeur d'une victoire. Très supérieure à toute évaluation heuristique possible
# pour qu'un mat soit toujours préféré à une simple amélioration de position.
WIN_SCORE = 1_000_000
INF = float("inf")

# Ordre statique des colonnes : les centrales d'abord. Au Puissance 4 le centre
# participe au plus grand nombre d'alignements, c'est donc le meilleur ordre a priori.
CENTER_ORDER = [3, 2, 4, 1, 5, 0, 6]

# Flags des bornes stockées dans la table de transposition.
TT_EXACT = 0   # valeur exacte du nœud
TT_LOWER = 1   # borne inférieure (échec haut / cutoff beta)
TT_UPPER = 2   # borne supérieure (échec bas)


def _build_windows() -> List[List[Tuple[int, int]]]:
    """Liste de toutes les fenêtres de 4 cases alignées du plateau.

    Calculée une seule fois (indépendante de l'occupation). La fonction
    d'évaluation note chaque fenêtre selon son potentiel d'alignement.
    """
    windows: List[List[Tuple[int, int]]] = []
    for r in range(ROWS):
        for c in range(COLS):
            if c + 4 <= COLS:  # horizontale
                windows.append([(r, c + k) for k in range(4)])
            if r + 4 <= ROWS:  # verticale
                windows.append([(r + k, c) for k in range(4)])
            if r + 4 <= ROWS and c + 4 <= COLS:  # diagonale montante /
                windows.append([(r + k, c + k) for k in range(4)])
            if r + 4 <= ROWS and c - 3 >= 0:  # diagonale descendante \
                windows.append([(r + k, c - k) for k in range(4)])
    return windows


_WINDOWS = _build_windows()

# Poids des configurations de fenêtre (n jetons à soi, le reste vide).
_WINDOW_WEIGHTS = {1: 1, 2: 10, 3: 50, 4: WIN_SCORE}
# Bonus par jeton dans la colonne centrale (contrôle du centre).
_CENTER_WEIGHT = 6
_CENTER_COL = COLS // 2


def evaluate(game: ConnectFour, player: int) -> int:
    """Évalue une position NON terminale du point de vue de `player`.

    Heuristique : pour chaque fenêtre de 4 cases, on récompense les alignements
    partiels (2/3 jetons à soi avec le reste vide) et on pénalise ceux de
    l'adversaire ; on ajoute un bonus de contrôle du centre.
    """
    opponent = PLAYER2 if player == PLAYER1 else PLAYER1
    board = game.board
    score = 0

    for window in _WINDOWS:
        p = o = 0
        for (r, c) in window:
            v = board[r][c]
            if v == player:
                p += 1
            elif v == opponent:
                o += 1
        # Fenêtre mixte : aucun des deux ne peut y compléter un alignement.
        if p and o:
            continue
        if p:
            score += _WINDOW_WEIGHTS[p]
        elif o:
            score -= _WINDOW_WEIGHTS[o]

    # Contrôle du centre.
    for r in range(ROWS):
        v = board[r][_CENTER_COL]
        if v == player:
            score += _CENTER_WEIGHT
        elif v == opponent:
            score -= _CENTER_WEIGHT

    return score


@dataclass
class SearchNode:
    """Nœud de l'arbre de recherche, enregistré pour la visualisation.

    `pruned=True` marque une branche qui n'a PAS été explorée à cause d'un cutoff
    alpha-beta (c'est exactement ce que l'on veut colorer dans la viz Knuth-Moore).
    """

    move: Optional[int]            # coup menant à ce nœud depuis le parent
    player_to_move: int            # joueur au trait dans ce nœud
    depth: int                     # profondeur restante de recherche
    value: Optional[float] = None  # valeur retournée (None si coupé)
    pruned: bool = False           # branche élaguée (non explorée)
    children: List["SearchNode"] = field(default_factory=list)


class AlphaBetaAgent(Agent):
    """Agent minimax/alpha-beta configurable.

    Paramètres d'ablation (pour les comparaisons de la viz) :
    - use_alpha_beta : active l'élagage αβ (sinon minimax exhaustif).
    - use_transposition : active la table de transposition (indexée par hash Zobrist).
    - use_move_ordering : trie les coups (centre d'abord + coup de la TT).

    Compteurs remis à zéro à chaque appel de recherche :
    - nodes : nœuds visités, cutoffs : coupures αβ, tt_hits : réutilisations de la TT.
    """

    def __init__(
        self,
        depth: int = 5,
        use_alpha_beta: bool = True,
        use_transposition: bool = True,
        use_move_ordering: bool = True,
        name: Optional[str] = None,
    ) -> None:
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.use_transposition = use_transposition
        self.use_move_ordering = use_move_ordering
        self.name = name or f"AlphaBeta(d={depth})"

        # Table de transposition : hash Zobrist -> (depth, value, flag, best_move).
        self._tt: Dict[int, Tuple[int, float, int, Optional[int]]] = {}

        # Compteurs d'instrumentation.
        self.nodes = 0
        self.cutoffs = 0
        self.tt_hits = 0

        # Enregistrement optionnel de l'arbre (pour la visualisation).
        self._record_tree = False
        self.last_tree: Optional[SearchNode] = None
        # Scores par colonne au dernier coup (pour l'affichage « ce que pense l'agent »).
        self.last_move_scores: Dict[int, float] = {}

    def reset(self) -> None:
        """Vide la table de transposition entre deux parties indépendantes."""
        self._tt.clear()

    # ------------------------------------------------------------------ #
    # Ordonnancement des coups
    # ------------------------------------------------------------------ #
    def _order_moves(self, legal: List[int], tt_move: Optional[int]) -> List[int]:
        """Trie les coups : coup de la TT d'abord, puis colonnes centrales."""
        if not self.use_move_ordering:
            return legal
        ordered = [c for c in CENTER_ORDER if c in legal]
        if tt_move is not None and tt_move in ordered:
            ordered.remove(tt_move)
            ordered.insert(0, tt_move)
        return ordered

    # ------------------------------------------------------------------ #
    # Negamax + alpha-beta + TT
    # ------------------------------------------------------------------ #
    def _negamax(
        self,
        game: ConnectFour,
        depth: int,
        alpha: float,
        beta: float,
        node: Optional[SearchNode],
    ) -> float:
        """Negamax avec alpha-beta et table de transposition.

        Retourne la valeur de la position du point de vue du joueur au trait.
        `node` (si non None) reçoit la trace de l'arbre pour la visualisation.
        """
        self.nodes += 1
        alpha_orig = alpha

        # --- Cas terminaux ------------------------------------------------
        winner = game.winner()
        if winner is not None:
            # Le gagnant est celui qui vient de jouer : le joueur au trait a donc
            # PERDU. On pénalise d'autant moins que la défaite est lointaine
            # (ply élevé) pour préférer les défaites tardives / victoires rapides.
            ply = len(game.move_history)
            value = -(WIN_SCORE - ply)
            if node is not None:
                node.value = value
            return value
        if game.is_full():
            if node is not None:
                node.value = 0
            return 0
        if depth == 0:
            value = evaluate(game, game.current_player)
            if node is not None:
                node.value = value
            return value

        # --- Sonde de la table de transposition --------------------------
        tt_move: Optional[int] = None
        if self.use_transposition:
            entry = self._tt.get(game.zobrist_hash)
            if entry is not None:
                e_depth, e_value, e_flag, e_move = entry
                tt_move = e_move
                if e_depth >= depth:
                    if e_flag == TT_EXACT:
                        self.tt_hits += 1
                        if node is not None:
                            node.value = e_value
                        return e_value
                    elif e_flag == TT_LOWER:
                        alpha = max(alpha, e_value)
                    elif e_flag == TT_UPPER:
                        beta = min(beta, e_value)
                    if self.use_alpha_beta and alpha >= beta:
                        self.tt_hits += 1
                        if node is not None:
                            node.value = e_value
                        return e_value

        # --- Exploration des coups ---------------------------------------
        legal = game.legal_moves()
        ordered = self._order_moves(legal, tt_move)

        best_value = -INF
        best_move: Optional[int] = None

        for i, col in enumerate(ordered):
            child = None
            if node is not None:
                child = SearchNode(
                    move=col,
                    player_to_move=PLAYER2 if game.current_player == PLAYER1 else PLAYER1,
                    depth=depth - 1,
                )
                node.children.append(child)

            game.play_move(col)
            value = -self._negamax(game, depth - 1, -beta, -alpha, child)
            game.undo_move()

            if value > best_value:
                best_value = value
                best_move = col
            if best_value > alpha:
                alpha = best_value

            # Coupure alpha-beta : inutile d'explorer les coups suivants.
            if self.use_alpha_beta and alpha >= beta:
                self.cutoffs += 1
                # Marque les coups restants comme branches élaguées (pour la viz).
                if node is not None:
                    for pruned_col in ordered[i + 1:]:
                        node.children.append(
                            SearchNode(
                                move=pruned_col,
                                player_to_move=(
                                    PLAYER2 if game.current_player == PLAYER1 else PLAYER1
                                ),
                                depth=depth - 1,
                                pruned=True,
                            )
                        )
                break

        # --- Stockage dans la table de transposition ---------------------
        if self.use_transposition:
            if best_value <= alpha_orig:
                flag = TT_UPPER
            elif best_value >= beta:
                flag = TT_LOWER
            else:
                flag = TT_EXACT
            self._tt[game.zobrist_hash] = (depth, best_value, flag, best_move)

        if node is not None:
            node.value = best_value
        return best_value

    # ------------------------------------------------------------------ #
    # Interface publique
    # ------------------------------------------------------------------ #
    def search(
        self, game: ConnectFour, record_tree: bool = False
    ) -> Tuple[int, float, Dict[int, float]]:
        """Cherche le meilleur coup à la racine.

        Renvoie (meilleure_colonne, valeur, scores_par_colonne). Remet à zéro les
        compteurs et, si record_tree=True, construit `self.last_tree`.
        Les scores par colonne sont calculés au niveau racine (utile pour la viz
        « évaluation par colonne »). Note : avec αβ, certaines valeurs de colonnes
        non gagnantes sont des bornes, pas des valeurs exactes.
        """
        self.nodes = 0
        self.cutoffs = 0
        self.tt_hits = 0

        work = game.copy()
        legal = work.legal_moves()

        root = SearchNode(move=None, player_to_move=work.current_player, depth=self.depth)
        ordered = self._order_moves(legal, None)

        alpha, beta = -INF, INF
        best_value = -INF
        best_move = ordered[0]
        scores: Dict[int, float] = {}

        for col in ordered:
            child = None
            if record_tree:
                child = SearchNode(
                    move=col,
                    player_to_move=PLAYER2 if work.current_player == PLAYER1 else PLAYER1,
                    depth=self.depth - 1,
                )
                root.children.append(child)

            work.play_move(col)
            value = -self._negamax(work, self.depth - 1, -beta, -alpha, child)
            work.undo_move()

            scores[col] = value
            if value > best_value:
                best_value = value
                best_move = col
            if best_value > alpha:
                alpha = best_value
            # Pas de cutoff à la racine : on veut un score pour chaque colonne.

        root.value = best_value
        if record_tree:
            self.last_tree = root
        self.last_move_scores = scores
        return best_move, best_value, scores

    def move(self, game: ConnectFour) -> int:
        best_move, _, _ = self.search(game)
        return best_move

    def count_nodes(self, game: ConnectFour, depth: Optional[int] = None) -> int:
        """Lance une recherche à profondeur donnée et renvoie le nombre de nœuds.

        Utilitaire pour la visualisation « nœuds vs profondeur » : permet de
        mesurer le coût de la recherche pour la configuration courante de l'agent.
        """
        saved_depth = self.depth
        if depth is not None:
            self.depth = depth
        try:
            self.reset()  # TT vide pour une mesure équitable
            self.search(game)
            return self.nodes
        finally:
            self.depth = saved_depth
