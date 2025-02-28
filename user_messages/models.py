from django.db import models
from user.models import User

class DemandeOrganisateur(models.Model):
    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("ACCEPTE", "Accepté"),
        ("REFUSE", "Refusé"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="demande_organisateur")
    nom_entreprise = models.CharField(max_length=255)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    numero_cni = models.CharField(max_length=50)
    photo_cni = models.ImageField(upload_to="cni/", blank=True, null=True)
    types_evenements = models.JSONField(default=list)
    taille_evenements = models.CharField(max_length=50)
    mode_financement = models.CharField(max_length=50)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="EN_ATTENTE")
    date_demande = models.DateTimeField(auto_now_add=True)
    commentaire_admin = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Demande de {self.user.nom} - {self.get_statut_display()}"
