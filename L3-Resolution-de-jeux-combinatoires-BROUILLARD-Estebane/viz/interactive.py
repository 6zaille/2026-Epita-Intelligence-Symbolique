"""Plateau interactif jouable dans le notebook.

L'humain joue contre l'agent de son choix. À chaque tour de l'agent, on affiche
« ce qu'il pense » (évaluation αβ / visites MCTS / Q-valeurs DQN) sous le plateau.

Ce module dépend d'ipywidgets et n'est donc à utiliser que dans le notebook ;
la logique de rendu pur (sans widgets) est dans `viz.board` et reste testable.

Usage dans le notebook :
    from viz.interactive import InteractiveGame
    InteractiveGame({"AlphaBeta": ab_agent, "MCTS": mcts_agent, "DQN": dqn_agent}).show()
"""

from __future__ import annotations

from typing import Dict, Optional

import matplotlib.pyplot as plt

from agents.base import Agent
from game.connect_four import COLS, PLAYER1, PLAYER2, ConnectFour
from viz.board import agent_thoughts, draw_board, draw_thoughts


class InteractiveGame:
    """Interface de jeu humain vs agent avec affichage de la réflexion de l'agent."""

    def __init__(self, agents: Dict[str, Agent], human_starts: bool = True) -> None:
        # Import local : ipywidgets n'est requis qu'à l'usage (pas aux tests).
        import ipywidgets as widgets

        self.widgets = widgets
        self.agents = agents
        self.human_starts = human_starts
        self.human_player = PLAYER1 if human_starts else PLAYER2
        self.agent_player = PLAYER2 if human_starts else PLAYER1

        self.game = ConnectFour()
        self.agent: Agent = next(iter(agents.values()))

        # --- Widgets ---
        self.agent_selector = widgets.Dropdown(
            options=list(agents.keys()), description="Adversaire :",
            style={"description_width": "initial"},
        )
        self.agent_selector.observe(self._on_agent_change, names="value")

        self.col_buttons = [
            widgets.Button(description=str(c), layout=widgets.Layout(width="44px"))
            for c in range(COLS)
        ]
        for c, btn in enumerate(self.col_buttons):
            btn.on_click(lambda _b, col=c: self._on_human_move(col))

        self.reset_button = widgets.Button(
            description="Nouvelle partie", button_style="info",
            layout=widgets.Layout(width="140px"),
        )
        self.reset_button.on_click(lambda _b: self._reset())

        self.status = widgets.HTML()
        self.board_out = widgets.Output()
        self.thoughts_out = widgets.Output()

        controls = widgets.HBox([self.agent_selector, self.reset_button])
        col_row = widgets.HBox([widgets.Label("Jouer colonne :")] + self.col_buttons)
        self.ui = widgets.VBox(
            [controls, col_row, self.status, self.board_out, self.thoughts_out]
        )

    # ------------------------------------------------------------------ #
    def show(self) -> None:
        self._reset()
        from IPython.display import display
        display(self.ui)
        # Pas de `return self.ui` : sinon Jupyter réaffiche la valeur retournée
        # (dernière expression de la cellule) et le widget apparaît en double.

    # ------------------------------------------------------------------ #
    def _on_agent_change(self, change) -> None:
        self.agent = self.agents[change["new"]]
        self._reset()

    def _reset(self) -> None:
        self.game = ConnectFour()
        self._refresh_buttons()
        # Si l'agent commence, il joue immédiatement.
        if not self.human_starts:
            self._agent_play()
        self._render()
        self._set_status("À vous de jouer.")

    def _on_human_move(self, col: int) -> None:
        if self.game.is_terminal() or not self.game.is_legal(col):
            return
        if self.game.current_player != self.human_player:
            return
        self.game.play_move(col)
        self._render()
        if self._check_end():
            return
        self._agent_play()
        self._render_thoughts_last()
        self._check_end()

    def _agent_play(self) -> None:
        if self.game.is_terminal():
            return
        # Calcule d'abord la pensée (sur l'état courant) puis joue le coup.
        self._last_thoughts = agent_thoughts(self.agent, self.game)
        col = self.agent.move(self.game)
        self.game.play_move(col)
        self._last_agent_col = col
        self._render()
        self._refresh_buttons()

    # ------------------------------------------------------------------ #
    def _check_end(self) -> bool:
        winner = self.game.winner()
        if winner is not None:
            who = "Vous avez gagné ! 🎉" if winner == self.human_player else "L'agent gagne."
            self._set_status(who)
            self._disable_columns()
            return True
        if self.game.is_full():
            self._set_status("Match nul.")
            self._disable_columns()
            return True
        return False

    def _refresh_buttons(self) -> None:
        legal = set(self.game.legal_moves())
        for c, btn in enumerate(self.col_buttons):
            btn.disabled = c not in legal or self.game.is_terminal()

    def _disable_columns(self) -> None:
        for btn in self.col_buttons:
            btn.disabled = True

    def _set_status(self, msg: str) -> None:
        self.status.value = f"<b>{msg}</b>"

    # ------------------------------------------------------------------ #
    def _render(self) -> None:
        self.board_out.clear_output(wait=True)
        with self.board_out:
            highlight = getattr(self, "_last_agent_col", None)
            fig, ax = draw_board(self.game, highlight_col=highlight)
            plt.show()

    def _render_thoughts_last(self) -> None:
        thoughts = getattr(self, "_last_thoughts", None)
        if thoughts is None:
            return
        scores, label = thoughts
        self.thoughts_out.clear_output(wait=True)
        with self.thoughts_out:
            fig, ax = draw_thoughts(scores, label, best_col=getattr(self, "_last_agent_col", None))
            fig.set_size_inches(6, 2.4)
            plt.show()
