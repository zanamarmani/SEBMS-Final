"""Unit tests for tariff slab calculation (single source of truth)."""
from decimal import Decimal

import pytest

from core.services.billing import calculate_bill_amount, payable_after_due_date
from tests.factories import TariffFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def tariff():
    return TariffFactory(price_100=3, price_200=4, price_300=5, price_above=6)


def test_zero_units(tariff):
    assert calculate_bill_amount(0, tariff) == Decimal("0.00")


def test_within_first_slab(tariff):
    assert calculate_bill_amount(50, tariff) == Decimal("150.00")


def test_exactly_100_units(tariff):
    assert calculate_bill_amount(100, tariff) == Decimal("300.00")


def test_second_slab_boundary(tariff):
    # 100*3 + 50*4
    assert calculate_bill_amount(150, tariff) == Decimal("500.00")


def test_third_slab(tariff):
    # 100*3 + 100*4 + 50*5
    assert calculate_bill_amount(250, tariff) == Decimal("950.00")


def test_above_300_slab(tariff):
    # 100*3 + 100*4 + 100*5 + 50*6
    assert calculate_bill_amount(350, tariff) == Decimal("1500.00")


def test_exact_300_units(tariff):
    assert calculate_bill_amount(300, tariff) == Decimal("1200.00")


def test_negative_units_rejected(tariff):
    with pytest.raises(ValueError):
        calculate_bill_amount(-1, tariff)


def test_missing_tariff_rejected():
    with pytest.raises(ValueError):
        calculate_bill_amount(100, None)


def test_late_fee_is_ten_percent():
    assert payable_after_due_date(Decimal("100.00")) == Decimal("110.00")
    assert payable_after_due_date(Decimal("770.00")) == Decimal("847.00")
