"""
Vanilla CFR and CFR+ implementations for Kuhn Poker.

CFR (Counterfactual Regret Minimization):
  At each info set, track cumulative regrets per action.
  Strategy = regret-matching: normalize positive regrets.
  Average strategy across iterations converges to Nash equilibrium.

CFR+:
  Regrets are floored at 0 (no negative cumulative regret).
  Uses alternating player updates.
  Linear weighting of strategies (iteration t has weight t).
"""

import numpy as np
from typing import Dict, Tuple
from .kuhn_poker import (
    is_terminal, current_player, terminal_utility,
    info_set_key, get_actions, CARDS, CARD_NAMES
)


class InfoSet:
    def __init__(self, n_actions: int):
        self.cumulative_regret = np.zeros(n_actions)
        self.cumulative_strategy = np.zeros(n_actions)

    def get_strategy(self, realization_weight: float) -> np.ndarray:
        pos = np.maximum(self.cumulative_regret, 0)
        total = pos.sum()
        if total > 0:
            strategy = pos / total
        else:
            strategy = np.ones(len(pos)) / len(pos)
        self.cumulative_strategy += realization_weight * strategy
        return strategy

    def get_average_strategy(self) -> np.ndarray:
        total = self.cumulative_strategy.sum()
        if total > 0:
            return self.cumulative_strategy / total
        return np.ones(len(self.cumulative_strategy)) / len(self.cumulative_strategy)


class CFR:
    def __init__(self):
        self.info_sets: Dict[str, InfoSet] = {}
        self.iteration = 0

    def _get_info_set(self, key: str, n_actions: int) -> InfoSet:
        if key not in self.info_sets:
            self.info_sets[key] = InfoSet(n_actions)
        return self.info_sets[key]

    def _cfr(self, cards: tuple, history: str, reach0: float, reach1: float) -> float:
        """Returns counterfactual utility for player 0."""
        if is_terminal(history):
            return terminal_utility(history, cards)

        player = current_player(history)
        actions = get_actions(history)
        n = len(actions)

        key = info_set_key(player, cards[player], history)
        node = self._get_info_set(key, n)

        reach = reach0 if player == 0 else reach1
        strategy = node.get_strategy(reach)

        action_utils = np.zeros(n)
        for i, action in enumerate(actions):
            next_h = history + action
            if player == 0:
                action_utils[i] = self._cfr(cards, next_h, reach0 * strategy[i], reach1)
            else:
                action_utils[i] = self._cfr(cards, next_h, reach0, reach1 * strategy[i])

        node_util = (strategy * action_utils).sum()

        # action_utils are always in player-0 perspective.
        # Regret for player i = u_i(action) - u_i(strategy).
        # For player 1: u_1 = -u_0, so regret = -action_util - (-node_util) = node_util - action_util.
        cf_reach = reach1 if player == 0 else reach0
        sign = 1 if player == 0 else -1
        for i in range(n):
            node.cumulative_regret[i] += sign * cf_reach * (action_utils[i] - node_util)

        return node_util

    def train(self, n_iterations: int) -> np.ndarray:
        """Run CFR for n_iterations. Returns game value history."""
        values = np.zeros(n_iterations)
        card_perms = [(c0, c1) for c0 in CARDS for c1 in CARDS if c0 != c1]
        n_deals = len(card_perms)

        for t in range(n_iterations):
            self.iteration += 1
            total_util = 0.0
            for cards in card_perms:
                total_util += self._cfr(cards, '', 1.0, 1.0)
            values[t] = total_util / n_deals

        return values

    def get_strategy_profile(self) -> Dict[str, np.ndarray]:
        return {k: v.get_average_strategy() for k, v in self.info_sets.items()}


class CFRPlus(CFR):
    """
    CFR+: cumulative regrets are floored at 0 after each update.
    Uses alternating updates (player 0 on even iterations, player 1 on odd).
    Linear weighting of the strategy sum (weight = iteration index).
    """

    def _get_info_set(self, key: str, n_actions: int) -> InfoSet:
        if key not in self.info_sets:
            self.info_sets[key] = InfoSet(n_actions)
        return self.info_sets[key]

    def _cfr_plus(self, cards: tuple, history: str, reach0: float, reach1: float,
                  updating_player: int, t: int) -> float:
        if is_terminal(history):
            return terminal_utility(history, cards)

        player = current_player(history)
        actions = get_actions(history)
        n = len(actions)

        key = info_set_key(player, cards[player], history)
        node = self._get_info_set(key, n)

        reach = reach0 if player == 0 else reach1
        pos = np.maximum(node.cumulative_regret, 0)
        total = pos.sum()
        strategy = pos / total if total > 0 else np.ones(n) / n

        if player == updating_player:
            node.cumulative_strategy += t * strategy

        action_utils = np.zeros(n)
        for i, action in enumerate(actions):
            next_h = history + action
            if player == 0:
                action_utils[i] = self._cfr_plus(
                    cards, next_h, reach0 * strategy[i], reach1, updating_player, t)
            else:
                action_utils[i] = self._cfr_plus(
                    cards, next_h, reach0, reach1 * strategy[i], updating_player, t)

        node_util = (strategy * action_utils).sum()

        if player == updating_player:
            cf_reach = reach1 if player == 0 else reach0
            sign = 1 if player == 0 else -1
            for i in range(n):
                node.cumulative_regret[i] = max(
                    0.0,
                    node.cumulative_regret[i] + sign * cf_reach * (action_utils[i] - node_util)
                )

        return node_util

    def train(self, n_iterations: int) -> np.ndarray:
        values = np.zeros(n_iterations)
        card_perms = [(c0, c1) for c0 in CARDS for c1 in CARDS if c0 != c1]
        n_deals = len(card_perms)

        for t in range(1, n_iterations + 1):
            self.iteration = t
            total_util = 0.0
            # Alternating updates
            for updating_player in [0, 1]:
                for cards in card_perms:
                    u = self._cfr_plus(cards, '', 1.0, 1.0, updating_player, t)
                    if updating_player == 0:
                        total_util += u
            values[t - 1] = total_util / n_deals

        return values
