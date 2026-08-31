"""What the cards will hand back, and when.

Card rewards are the household's Christmas fund: they accrue all year and are
cashed in one go in November, a few weeks before the gift bucket is emptiest.
The planner could not see them, so it asked for money that was already coming.

They have to be read from the balance snapshots rather than from transactions
because the transaction record is unreliable — a redemption was recorded as a
`Statement Credit` in 2019, 2020, 2021 and 2024, and not in 2025, though the
balances plainly fell by 1,107.55 that November.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from planning.services.rewards import reward_outlook

pytestmark = [pytest.mark.service, pytest.mark.django_db]


@pytest.fixture
def card(db):
    from accounts.models import Account, AccountType, Bank

    account_type, _ = AccountType.objects.get_or_create(
        account_type="Credit Card"
    )
    bank, _ = Bank.objects.get_or_create(bank_name="Test Bank")
    return Account.objects.create(
        account_name="Test Card", account_type=account_type, bank=bank
    )


def snapshot(card, when, amount):
    from accounts.models import Reward

    return Reward.objects.create(
        reward_account=card, reward_date=when, reward_amount=Decimal(str(amount))
    )


def test_accrual_is_the_sum_of_the_gains_not_the_net_change(card):
    """A card that earns 400 and spends 400 earns 400, not nothing.

    Netting first and last balances would report a card that genuinely brings
    in 470 a year as bringing in nothing at all, because the redemption
    cancels the accrual by design.
    """
    today = date(2026, 8, 31)
    snapshot(card, today - timedelta(days=360), 0)
    snapshot(card, today - timedelta(days=300), 200)
    snapshot(card, today - timedelta(days=280), 400)
    snapshot(card, today - timedelta(days=270), 0)  # redeemed
    snapshot(card, today - timedelta(days=100), 300)

    outlook = reward_outlook(today)

    assert outlook.accrual_per_year > Decimal("600")
    assert outlook.current_balance == Decimal("300.00")


def test_a_redemption_is_a_cliff_not_a_wobble(card):
    today = date(2026, 8, 31)
    snapshot(card, today - timedelta(days=300), 500)
    snapshot(card, today - timedelta(days=299), Decimal("499.50"))  # noise
    snapshot(card, today - timedelta(days=200), 20)  # redeemed
    snapshot(card, today - timedelta(days=100), 120)

    outlook = reward_outlook(today)

    assert len(outlook.past_redemptions) == 1
    assert outlook.past_redemptions[0]["amount"] == Decimal("479.50")


def test_the_expected_amount_includes_what_will_still_accrue(card):
    """The figure that matters is the balance on the day it is cashed in, not
    the balance today — there are months of earning left before then."""
    today = date(2026, 8, 31)
    snapshot(card, today - timedelta(days=365), 0)
    snapshot(card, today - timedelta(days=300), 600)
    snapshot(card, today - timedelta(days=290), 0)  # a November-ish redemption
    snapshot(card, today, 500)

    outlook = reward_outlook(today)

    assert outlook.redemption_on is not None
    assert outlook.redemption_on > today
    assert outlook.expected_amount > outlook.current_balance


def test_no_history_means_no_claim(card):
    """One snapshot is not a rhythm, and guessing at a redemption date from it
    would put a four-figure inflow on the path on the strength of nothing."""
    today = date(2026, 8, 31)
    snapshot(card, today, 500)

    outlook = reward_outlook(today)

    assert outlook.redemption_on is None
    assert outlook.expected_amount == Decimal("0.00")
