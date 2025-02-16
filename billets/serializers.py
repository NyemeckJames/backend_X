from rest_framework import serializers
from .models import Billet

class BilletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billet
        fields = ['id', 'evenement', 'participant', 'type_billet', 'prix', 'date_achat', 'est_annule']
        read_only_fields = ['id', 'date_achat']
