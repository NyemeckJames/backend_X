from rest_framework import serializers
from .models import Evenement

class EvenementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evenement
        fields = '__all__'  # Inclut tous les champs du modèle
        read_only_fields = ['id', 'date_creation']  # Ces champs ne seront pas modifiables
