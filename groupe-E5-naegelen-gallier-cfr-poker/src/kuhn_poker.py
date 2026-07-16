"""
Kuhn Poker game tree for CFR.

Rules: 2 players, 3 cards (J=0, Q=1, K=2), ante 1 chip each.
Action sequence: check(c) or bet(b). If bet: fold(f) or call(c).
Terminal histories: cc, bc, bf, bcf (wait — let's be precise):
  - cc: showdown, higher card wins 1 chip
  - bc: higher card wins 2 chips (caller wins if higher)
  - bf: bettor wins 1 chip (folder's ante)
  - bbc: showdown, higher card wins 2 chips... wait

Standard Kuhn Poker action encoding:
Player 0 acts first.
  - p (pass/check) or b (bet)
If p: player 1 acts
  - p: showdown (cc)
  - b: player 0 acts again
    - p: fold (cbf -> p1 wins 1)
    - b: showdown (cbb -> higher card wins 2)
If b: player 1 acts
  - p: fold (bp -> p0 wins 1)
  - b: showdown (bb -> higher card wins 2)

Information sets: card + history visible to that player.
"""

import numpy as np
from itertools import permutations

CARDS = [0, 1, 2]  # J, Q, K
CARD_NAMES = ['J', 'Q', 'K']


def is_terminal(history: str) -> bool:
    if history.endswith('pp'):
        return True
    if history.endswith('bp'):
        return True
    if history.endswith('bb'):
        return True
    if history.endswith('pbp'):
        return True
    if history.endswith('pbb'):
        return True
    return False


def current_player(history: str) -> int:
    """Returns 0 or 1 — whose turn it is."""
    return len(history) % 2


def terminal_utility(history: str, cards: tuple) -> float:
    """Utility for player 0 at a terminal node."""
    c0, c1 = cards
    higher_wins = 1 if c0 > c1 else -1

    if history == 'pp':
        return higher_wins
    if history == 'bp':
        return 1   # p1 folded, p0 wins ante
    if history == 'bb':
        return 2 * higher_wins
    if history == 'pbp':
        return -1  # p0 folded after p1 bet
    if history == 'pbb':
        return 2 * higher_wins
    raise ValueError(f"Unknown terminal history: {history}")


def info_set_key(player: int, card: int, history: str) -> str:
    return f"{CARD_NAMES[card]}:{history}"


def get_actions(history: str) -> list:
    """Valid actions at a non-terminal node."""
    if history in ('', 'p'):
        return ['p', 'b']
    if history in ('b', 'pb'):
        return ['p', 'b']  # p=fold, b=call
    raise ValueError(f"No actions for: {history}")
