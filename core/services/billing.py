"""Tariff slab billing — single source of truth for all bill-amount math.

Business rules (unchanged from legacy):
- Slabs: first 100 units @ price_100, next 100 @ price_200, next 100 @
  price_300, everything above 300 @ price_above.
- Due date term: 15 days after the bill date.
- Late fee: 10% of the payable amount when paid after the due date.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from SDO.models import Tariff

CENT = Decimal("0.01")
LATE_FEE_MULTIPLIER = Decimal("1.10")
DUE_TERM_DAYS = 15


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_bill_amount(units: Decimal | int | float, tariff: Tariff) -> Decimal:
    """Compute the slab-based bill amount for the consumed units."""
    if tariff is None:
        raise ValueError("Tariff is required to calculate a bill.")

    remaining = Decimal(str(units))
    if remaining < 0:
        raise ValueError("Consumed units cannot be negative.")

    total = Decimal("0.00")
    tiers: list[tuple[Optional[Decimal], Decimal]] = [
        (Decimal("100"), tariff.price_100),
        (Decimal("100"), tariff.price_200),
        (Decimal("100"), tariff.price_300),
        (None, tariff.price_above),
    ]

    for slab_size, rate in tiers:
        if remaining <= 0:
            break
        if slab_size is None:
            total += remaining * rate
            break
        if remaining > slab_size:
            total += slab_size * rate
            remaining -= slab_size
        else:
            total += remaining * rate
            break

    return _quantize(total)


def payable_after_due_date(payable_amount: Decimal) -> Decimal:
    """Amount payable once the due date has passed (10% late fee)."""
    return _quantize(Decimal(str(payable_amount)) * LATE_FEE_MULTIPLIER)
