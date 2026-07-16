"""
Leduc Hold'em — simplified for CFR.

Rules:
- 6 cards: J, Q, K (×2 copies)
- 2 players, ante 1 chip each
- Round 1: each player gets 1 private card. Bet up to 2 chips.
- Public card revealed.
- Round 2: Bet up to 4 chips.
- Showdown: pair > higher card.

Actions: p (check/pass), b (bet), f (fold), c (call).
We implement a compact version with a fixed raise size.

State: (private_card_p0, private_card_p1, public_card, history_r1, history_r2)
Information set: private_card + public_card (if revealed) + full history visible to player.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple

CARDS = [0, 1, 2]  # J=0, Q=1, K=2
CARD_NAMES = ['J', 'Q', 'K']

# Two copies of each card
DECK = [0, 0, 1, 1, 2, 2]

BET_SIZE_R1 = 2
BET_SIZE_R2 = 4


class LeducState:
    def __init__(self, cards: Tuple[int, int, int], history: str = ''):
        # cards = (p0_private, p1_private, public)
        self.cards = cards
        self.history = history  # encodes both rounds, '/' separates rounds

    @property
    def round(self) -> int:
        return 1 if '/' not in self.history else 2

    @property
    def round1_history(self) -> str:
        if '/' not in self.history:
            return self.history
        return self.history.split('/')[0]

    @property
    def round2_history(self) -> str:
        if '/' not in self.history:
            return ''
        return self.history.split('/')[1]

    def current_player(self) -> int:
        h = self.round1_history if self.round == 1 else self.round2_history
        return len(h) % 2

    def pot(self) -> int:
        pot = 2  # antes
        h1 = self.round1_history
        bets_r1 = h1.count('b') + h1.count('c')
        pot += bets_r1 * BET_SIZE_R1
        if '/' in self.history:
            h2 = self.round2_history
            bets_r2 = h2.count('b') + h2.count('c')
            pot += bets_r2 * BET_SIZE_R2
        return pot


def _round_terminal(h: str) -> bool:
    """Check if a single-round history is terminal."""
    if h.endswith('pp'):
        return True  # check-check
    if h.endswith('bp'):
        return True  # bet-fold
    if h.endswith('bc'):
        return True  # bet-call
    if h.endswith('pbp'):
        return True  # check-bet-fold
    if h.endswith('pbc'):
        return True  # check-bet-call
    return False


def is_terminal(history: str) -> bool:
    if '/' not in history:
        # Still in round 1
        if 'f' in history or history.endswith('bp') or history.endswith('pbp'):
            # Fold ends game
            if history.endswith('bp') or history.endswith('pbp'):
                return True
            return False
        return _round_terminal(history)
    r1, r2 = history.split('/')
    return _round_terminal(r2)


def is_fold(history: str) -> bool:
    """Did someone fold?"""
    if history.endswith('bp') or history.endswith('pbp'):
        return True
    if '/' in history:
        r2 = history.split('/')[1]
        if r2.endswith('bp') or r2.endswith('pbp'):
            return True
    return False


def get_actions(history: str) -> List[str]:
    if '/' not in history:
        h = history
    else:
        h = history.split('/')[1]

    if h == '' or h == 'p':
        return ['p', 'b']
    if h == 'b':
        return ['p', 'c']  # fold (p) or call (c)
    if h == 'pb':
        return ['p', 'c']  # fold or call
    return []


def current_player(history: str) -> int:
    if '/' not in history:
        h = history
    else:
        h = history.split('/')[1]
    return len(h) % 2


def _hand_rank(private: int, public: int) -> int:
    """Higher is better. Pair beats high card."""
    if private == public:
        return 10 + private  # pair
    return private  # high card


def terminal_utility(history: str, cards: Tuple[int, int, int]) -> float:
    """Utility for player 0."""
    c0, c1, pub = cards
    pot = 2  # antes

    # Compute pot from round 1
    r1 = history.split('/')[0] if '/' in history else history
    pot += r1.count('b') * BET_SIZE_R1 + r1.count('c') * BET_SIZE_R1

    if '/' in history:
        r2 = history.split('/')[1]
        pot += r2.count('b') * BET_SIZE_R2 + r2.count('c') * BET_SIZE_R2

    # Who folded?
    if is_fold(history):
        folder_player = current_player(history[:-1] if history else history)
        if '/' in history:
            h2 = history.split('/')[1]
            if h2:
                folder_player = current_player(history[:-1])
        # The player who just acted (last char before the terminal) folded
        # Actually: last action 'p' after a 'b' means fold
        last_h = history.split('/')[-1]
        # Count actions in last round
        n_acts = len(last_h)
        folder = (n_acts - 1) % 2  # player who did the last action
        if folder == 0:
            return -(pot / 2)  # p0 folded, loses ante
        else:
            return pot / 2   # p1 folded, p0 wins

    # Showdown
    r0 = _hand_rank(c0, pub)
    r1_rank = _hand_rank(c1, pub)
    if r0 > r1_rank:
        return pot / 2
    elif r1_rank > r0:
        return -pot / 2
    return 0.0  # tie (impossible with distinct cards, but safe)


def info_set_key(player: int, private: int, public: Optional[int], history: str) -> str:
    pub_str = CARD_NAMES[public] if public is not None else ''
    return f"{CARD_NAMES[private]}{pub_str}:{history}"


class LeducCFR:
    def __init__(self):
        self.info_sets: Dict[str, 'InfoSet'] = {}
        self.nodes_visited = 0

    def _get_node(self, key: str, n: int):
        from .cfr import InfoSet
        if key not in self.info_sets:
            self.info_sets[key] = InfoSet(n)
        return self.info_sets[key]

    def _cfr(self, cards: Tuple[int, int, int], history: str,
             reach0: float, reach1: float) -> float:
        self.nodes_visited += 1

        if is_terminal(history):
            return terminal_utility(history, cards)

        player = current_player(history)
        actions = get_actions(history)
        n = len(actions)

        c0, c1, pub = cards
        # Public card only known after round 1 ends
        round_num = 1 if '/' not in history else 2
        pub_visible = pub if round_num == 2 else None

        key = info_set_key(player, c0 if player == 0 else c1, pub_visible, history)
        node = self._get_node(key, n)

        reach = reach0 if player == 0 else reach1
        strategy = node.get_strategy(reach)

        action_utils = np.zeros(n)
        for i, action in enumerate(actions):
            # Check if this action transitions between rounds
            new_h = history + action
            r1 = new_h.split('/')[0] if '/' not in new_h else new_h.split('/')[0]
            if '/' not in new_h and _round_terminal(new_h) and not is_fold(new_h):
                new_h = new_h + '/'  # transition to round 2

            if player == 0:
                action_utils[i] = self._cfr(cards, new_h, reach0 * strategy[i], reach1)
            else:
                action_utils[i] = self._cfr(cards, new_h, reach0, reach1 * strategy[i])

        node_util = (strategy * action_utils).sum()
        cf_reach = reach1 if player == 0 else reach0
        for i in range(n):
            node.cumulative_regret[i] += cf_reach * (action_utils[i] - node_util)

        return node_util

    def train(self, n_iterations: int):
        from itertools import permutations
        # All deals: choose 3 distinct cards from deck positions (accounting for duplicates)
        deals = []
        seen = set()
        for c0 in CARDS:
            for c1 in CARDS:
                for pub in CARDS:
                    cards_sorted = tuple(sorted([c0, c1, pub]))
                    # Allow pairs (two copies exist), but not triplets
                    counts = {0: 0, 1: 0, 2: 0}
                    for c in [c0, c1, pub]:
                        counts[c] += 1
                    if any(v > 2 for v in counts.values()):
                        continue
                    deals.append((c0, c1, pub))

        values = np.zeros(n_iterations)
        self.nodes_visited = 0

        for t in range(n_iterations):
            total = 0.0
            for cards in deals:
                total += self._cfr(cards, '', 1.0, 1.0)
            values[t] = total / len(deals)

        return values, len(deals)
