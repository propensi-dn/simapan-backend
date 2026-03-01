from django.db.models.signals import post_save
from django.dispatch import receiver

from members.models import MemberProfile
from users.models import User, UserRole


@receiver(post_save, sender=User)
def create_member_profile(sender, instance: User, created: bool, **kwargs):
    if not created:
        return

    if instance.role == UserRole.MEMBER:
        MemberProfile.objects.get_or_create(user=instance)
