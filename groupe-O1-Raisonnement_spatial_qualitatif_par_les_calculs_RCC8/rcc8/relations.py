from enum import Enum

"""
règle RCC8 (composition)

Si :

A — R1 — B
B — R2 — C

Alors :

A — (R1 ∘ R2) — C

"""


class RCC8(Enum):
    """
    RCC8 (Region Connection Calculus) relations.
    Topological relations between spatial regions.
    """

    DC = "DC"      # Disconnected
    EC = "EC"      # Externally Connected
    PO = "PO"      # Partial Overlap
    EQ = "EQ"      # Equal
    TPP = "TPP"    # Tangential Proper Part
    NTPP = "NTPP"  # Non-Tangential Proper Part
    TPPI = "TPPI"  # Inverse of TPP
    NTPPI = "NTPPI"  # Inverse of NTPP


# ----------------------------
# Symmetric relations
# ----------------------------

_SYMMETRIC_RELATIONS = {
    RCC8.DC,
    RCC8.EC,
    RCC8.PO,
    RCC8.EQ,
}


def is_symmetric(r: RCC8) -> bool:
    """
    Check if a relation is symmetric.
    """
    return r in _SYMMETRIC_RELATIONS


# ----------------------------
# Helpers
# ----------------------------

def inverse_relation(r: RCC8) -> RCC8:
    """
    Retourne la relation inverse RCC8.

    Exemple:
        TPP  -> TPPI
        TPPI -> TPP
        EC   -> EC (symétrique)
    """

    if r == RCC8.TPP:
        return RCC8.TPPI

    if r == RCC8.TPPI:
        return RCC8.TPP

    if r == RCC8.NTPP:
        return RCC8.NTPPI

    if r == RCC8.NTPPI:
        return RCC8.NTPP

    # relations symétriques (elles sont leur propre inverse)
    return r