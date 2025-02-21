from django.db.models.signals import post_save
from django.dispatch import receiver
from evenements.models import Evenement
from room.models import Room

@receiver(post_save, sender=Evenement)
def create_chatroom(sender, instance, created, **kwargs):
    if created:
        Room.objects.create(evenement=instance)
