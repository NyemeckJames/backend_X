from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    evenement_id = serializers.IntegerField(source="evenement.id", read_only=True)
    evenement_titre = serializers.CharField(source="evenement.titre", read_only=True)
    organisateur_nom = serializers.CharField(source="organisateur.nom", read_only=True)
    organisateur_prenom = serializers.CharField(source="organisateur.prenom", read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'message', 'date_envoi', 'evenement_id', 'evenement_titre', 'organisateur_nom', 'organisateur_prenom']
