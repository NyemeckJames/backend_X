

# Create your models here.
from django.db import models
from user.models import User
from evenements.models import Evenement  # Import du modèle Evenement


class Notification(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name="notifications")
    organisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_envoyees")
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    participants_recipients = models.ManyToManyField(User, through='NotificationParticipant', related_name="notifications_recues")

    def __str__(self):
        return f"Notif pour {self.evenement.titre} - {self.message[:30]}..."


class NotificationParticipant(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="recipients")
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_participant")
    vu = models.BooleanField(default=False)  # Permet de savoir si le participant a lu la notification
    date_vue = models.DateTimeField(null=True, blank=True)  # Optionnel : stocker la date de lecture

    def __str__(self):
        return f"Notification '{self.notification.message[:30]}...' pour {self.participant.nom} {self.participant.prenom}"

