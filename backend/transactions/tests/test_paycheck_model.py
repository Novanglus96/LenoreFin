import pytest
from transactions.models import Paycheck
from administration.models import Payee


@pytest.mark.django_db
def test_paycheck_creation():
    payee = Payee.objects.create(payee_name="Test Payee")
    paycheck = Paycheck.objects.create(
        gross=1.00,
        net=1.00,
        taxes=1.00,
        health=1.00,
        pension=1.00,
        fsa=1.00,
        dca=1.00,
        union_dues=1.00,
        four_fifty_seven_b=1.00,
        payee=payee,
    )

    assert paycheck.id is not None
    assert paycheck.gross == 1.00
    assert paycheck.net == 1.00
    assert paycheck.taxes == 1.00
    assert paycheck.health == 1.00
    assert paycheck.pension == 1.00
    assert paycheck.fsa == 1.00
    assert paycheck.dca == 1.00
    assert paycheck.union_dues == 1.00
    assert paycheck.four_fifty_seven_b == 1.00
    assert paycheck.payee == payee


@pytest.mark.django_db
def test_paycheck_defaults():
    paycheck = Paycheck.objects.create()

    assert paycheck.id is not None
    assert paycheck.gross == 0.00
    assert paycheck.net == 0.00
    assert paycheck.taxes == 0.00
    assert paycheck.health == 0.00
    assert paycheck.pension == 0.00
    assert paycheck.fsa == 0.00
    assert paycheck.dca == 0.00
    assert paycheck.union_dues == 0.00
    assert paycheck.four_fifty_seven_b == 0.00
    assert paycheck.payee is None


@pytest.mark.django_db
def test_payee_foreign_key_set_null_delete():
    payee = Payee.objects.create(payee_name="Test Payee")
    paycheck = Paycheck.objects.create(
        gross=1.00,
        net=1.00,
        taxes=1.00,
        health=1.00,
        pension=1.00,
        fsa=1.00,
        dca=1.00,
        union_dues=1.00,
        four_fifty_seven_b=1.00,
        payee=payee,
    )

    assert paycheck.id is not None
    assert paycheck.payee is not None
    payee.delete()
    paycheck.refresh_from_db()
    assert paycheck.payee is None
