from django.db import models
from django.contrib.auth import get_user_model
from evenements.models import Evenement

from user.models import User

class Room(models.Model):
    evenement = models.OneToOneField(Evenement, on_delete=models.CASCADE, related_name="chat_room")

    def __str__(self):
        return f"Chatroom - {self.evenement.titre}"

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room.evenement.titre} - {self.sender.nom} {self.sender.prenom}"
