import datetime
import pytest
from accounts.models import Reward
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
@pytest.mark.unit
def test_reward_creation(test_checking_account):
    reward = Reward.objects.create(
        reward_date=datetime.date(2024, 1, 1),
        reward_amount=50.00,
        reward_account=test_checking_account,
    )

    assert reward.id is not None
    assert reward.reward_amount == 50.00
    assert reward.reward_date == datetime.date(2024, 1, 1)
    assert reward.reward_account == test_checking_account


@pytest.mark.django_db
@pytest.mark.unit
def test_reward_default_amount(test_checking_account):
    """Reward should default reward_amount to 0.00 when not provided."""
    reward = Reward.objects.create(reward_account=test_checking_account)

    assert reward.reward_amount == 0


@pytest.mark.django_db
@pytest.mark.unit
def test_reward_default_date(test_checking_account):
    """Reward should default reward_date to today when not supplied."""
    reward = Reward.objects.create(reward_account=test_checking_account)

    assert reward.reward_date == current_date()


@pytest.mark.django_db
@pytest.mark.unit
def test_reward_string_representation(test_checking_account):
    """Ensure __str__ returns the expected formatted string."""
    reward = Reward.objects.create(
        reward_amount=10,
        reward_date=datetime.date(2024, 5, 20),
        reward_account=test_checking_account,
    )

    expected = "2024-05-20 : Test Checking Account ($10)"
    assert str(reward) == expected


@pytest.mark.django_db
@pytest.mark.unit
def test_reward_foreign_key_cascade_delete(test_checking_account):
    """Rewards should be removed if their account is deleted."""
    Reward.objects.create(reward_amount=5, reward_account=test_checking_account)

    assert Reward.objects.count() == 1

    test_checking_account.delete()

    assert Reward.objects.count() == 0
