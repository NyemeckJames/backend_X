from rest_framework import serializers
from .models import DemandeOrganisateur

class DemandeOrganisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeOrganisateur
        fields = ["nom_entreprise", "facebook", "twitter", "numero_cni", "photo_cni", "types_evenements", "taille_evenements", "mode_financement"]
