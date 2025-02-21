from django.db import models
from user.models import User
# Create your models here.
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Evenement(models.Model):
    # Identifiant unique de l'événement
    id = models.AutoField(primary_key=True)

    # Détails de l'événement
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_heure = models.DateTimeField()
    lieu = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacite_max = models.IntegerField()
    date_creation = models.DateTimeField(auto_now_add=True)
    # Nouveau champ pour la photo de l'événement
    photo = models.ImageField(upload_to='evenements/', null=True, blank=True)
    evenementLibre = models.BooleanField(default=False)
    prix = models.IntegerField(default=20000)

    # Lien avec l'utilisateur (l'organisateur)
    organisateur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="evenements"
    )

    # Pour la gestion des billets associés à l'événement
    billets_disponibles = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.titre} - {self.organisateur.nom} {self.organisateur.prenom}"
    
    class Meta:
        ordering = ["date_heure"]  # Tri des événements par date de l'événement
        
import evenements.signals

