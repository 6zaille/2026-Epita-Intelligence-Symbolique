"""
Best-response oracle for Kuhn Poker.

Exploitability = BR_value(p0 against sigma_1) + BR_value(p1 against sigma_0)
At Nash equilibrium, exploitability = 0.

Correct algorithm for imperfect information games:
  For each info set I of the best-responder, compute for each action a:
    q(I, a) = sum_{deals consistent with I} reach_opp(deal, I) * u_i(deal, take action a here, then play BR downstream)
  BR strategy: argmax_a q(I, a)

  This requires a bottom-up traversal: deeper info sets are resolved first.
"""

import numpy as np
from typing import Dict, Optional
from collections import defaultdict
from .kuhn_poker import (
    is_terminal, current_player, terminal_utility,
    info_set_key, get_actions, CARDS
)

CARD_PERMS = [(c0, c1) for c0 in CARDS for c1 in CARDS if c0 != c1]


def best_response_value(strategy_profile: Dict[str, np.ndarray],
                        responding_player: int) -> float:
    """
    Compute best-response expected utility for `responding_player`
    against the fixed strategy of the other player.
    Correctly handles imperfect information: the best-response strategy
    is a function of information sets, not individual deals.
    """
    fixed_player = 1 - responding_player

    # Accumulate reach-weighted action utilities for each responding-player info set.
    # The key insight: we must accumulate across ALL deals with the same info set
    # before choosing the best action.
    infoset_action_sums: Dict[str, np.ndarray] = {}

    def get_util_subtree(cards: tuple, history: str) -> float:
        """
        Value for responding_player starting from `history`,
        assuming fixed player follows strategy_profile
        and responding player follows the BR strategy (from infoset_action_sums).
        """
        if is_terminal(history):
            u = terminal_utility(history, cards)
            return u if responding_player == 0 else -u

        player = current_player(history)
        actions = get_actions(history)
        n = len(actions)
        key = info_set_key(player, cards[player], history)

        if player == fixed_player:
            strategy = strategy_profile.get(key, np.ones(n) / n)
        else:
            sums = infoset_action_sums.get(key)
            if sums is not None and sums.max() != sums.min():
                strategy = np.zeros(n)
                strategy[np.argmax(sums)] = 1.0
            else:
                strategy = np.ones(n) / n

        return sum(strategy[i] * get_util_subtree(cards, history + a)
                   for i, a in enumerate(actions))

    def traverse(cards: tuple, history: str, reach_opp: float):
        """
        Bottom-up traversal: recurse into subtrees first,
        then accumulate action values at responding-player info sets.
        """
        if is_terminal(history):
            return

        player = current_player(history)
        actions = get_actions(history)
        n = len(actions)

        if player == fixed_player:
            key = info_set_key(fixed_player, cards[fixed_player], history)
            strategy = strategy_profile.get(key, np.ones(n) / n)
            for i, a in enumerate(actions):
                if strategy[i] > 0:
                    traverse(cards, history + a, reach_opp * strategy[i])
        else:
            key = info_set_key(responding_player, cards[responding_player], history)
            if key not in infoset_action_sums:
                infoset_action_sums[key] = np.zeros(n)

            # Recurse into all subtrees first (builds infoset_action_sums for deeper nodes)
            for a in actions:
                traverse(cards, history + a, reach_opp)

            # Now compute action values using the (already-populated) BR for deeper nodes
            for i, a in enumerate(actions):
                v = get_util_subtree(cards, history + a)
                infoset_action_sums[key][i] += reach_opp * v

    # Build action value sums across all deals
    for cards in CARD_PERMS:
        traverse(cards, '', 1.0)

    # Compute expected value under BR strategy vs fixed player's strategy
    def compute_br_value(cards: tuple, history: str) -> float:
        if is_terminal(history):
            u = terminal_utility(history, cards)
            return u if responding_player == 0 else -u

        player = current_player(history)
        actions = get_actions(history)
        n = len(actions)
        key = info_set_key(player, cards[player], history)

        if player == fixed_player:
            strategy = strategy_profile.get(key, np.ones(n) / n)
        else:
            sums = infoset_action_sums.get(key, np.zeros(n))
            strategy = np.zeros(n)
            strategy[np.argmax(sums)] = 1.0

        return sum(strategy[i] * compute_br_value(cards, history + a)
                   for i, a in enumerate(actions))

    total = sum(compute_br_value(cards, '') for cards in CARD_PERMS)
    return total / len(CARD_PERMS)


def exploitability(strategy_profile: Dict[str, np.ndarray]) -> float:
    """
    Total exploitability: sum of best-response gains for both players.
    = 0 at Nash equilibrium.
    """
    br0 = best_response_value(strategy_profile, 0)
    br1 = best_response_value(strategy_profile, 1)
    return br0 + br1
