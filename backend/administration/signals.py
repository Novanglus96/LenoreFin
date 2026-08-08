from django.db.models.signals import post_save
from django.dispatch import receiver
from administration.models import Message
from core.broadcast import broadcast_invalidate


@receiver(post_save, sender=Message)
def message_saved(sender, instance, created, **kwargs):
    if created:
        group = f"user_{instance.user.pk}" if instance.user_id else "global"
        broadcast_invalidate(["messages"], group=group)
