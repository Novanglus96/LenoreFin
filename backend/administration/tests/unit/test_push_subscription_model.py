import pytest
from django.contrib.auth.models import User
from administration.models import PushSubscription


def make_user(username="pushuser"):
    return User.objects.create_user(username=username, password="pass")


@pytest.mark.django_db
def test_push_subscription_creation():
    user = make_user()
    sub = PushSubscription.objects.create(
        user=user,
        endpoint="https://push.example.com/sub/abc123",
        p256dh="fakep256dh",
        auth="fakeauth",
    )

    assert sub.user == user
    assert sub.endpoint == "https://push.example.com/sub/abc123"
    assert sub.p256dh == "fakep256dh"
    assert sub.auth == "fakeauth"
    assert sub.created_at is not None


@pytest.mark.django_db
def test_push_subscription_string_representation():
    user = make_user()
    sub = PushSubscription.objects.create(
        user=user,
        endpoint="https://push.example.com/sub/abc123",
        p256dh="key",
        auth="auth",
    )

    assert str(user) in str(sub)
    assert "https://push.example.com/sub/abc123"[:60] in str(sub)


@pytest.mark.django_db
def test_push_subscription_endpoint_unique():
    user = make_user()
    PushSubscription.objects.create(
        user=user,
        endpoint="https://push.example.com/unique",
        p256dh="key",
        auth="auth",
    )

    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        PushSubscription.objects.create(
            user=user,
            endpoint="https://push.example.com/unique",
            p256dh="key2",
            auth="auth2",
        )


@pytest.mark.django_db
def test_push_subscription_cascade_delete():
    user = make_user()
    sub = PushSubscription.objects.create(
        user=user,
        endpoint="https://push.example.com/cascade",
        p256dh="key",
        auth="auth",
    )
    sub_id = sub.id

    user.delete()

    assert not PushSubscription.objects.filter(id=sub_id).exists()


@pytest.mark.django_db
def test_push_subscription_multiple_per_user():
    user = make_user()
    PushSubscription.objects.create(
        user=user, endpoint="https://push.example.com/1", p256dh="k1", auth="a1"
    )
    PushSubscription.objects.create(
        user=user, endpoint="https://push.example.com/2", p256dh="k2", auth="a2"
    )

    assert PushSubscription.objects.filter(user=user).count() == 2
