from rest_framework import serializers
from .models import Evenement

class EvenementSerializer(serializers.ModelSerializer):
    organisateur_nom = serializers.CharField(source="organisateur.nom", read_only=True)
    organisateur_prenom = serializers.CharField(source="organisateur.prenom", read_only=True)
    organisateur_telephone = serializers.CharField(source="organisateur.telephone", read_only=True)

    class Meta:
        model = Evenement
        fields = [
            "id",
            "titre",
            "description",
            "date_heure",
            "date_creation",
            "lieu",
            "latitude",
            "longitude",
            "capacite_max",
            "photo",
            "evenementLibre",
            "prix",
            "billets_disponibles",
            "organisateur",
            "organisateur_nom",
            "organisateur_prenom",
            "organisateur_telephone",
        ]
        extra_kwargs = {
            "organisateur": {"required": True},  # Rendre obligatoire
        }
