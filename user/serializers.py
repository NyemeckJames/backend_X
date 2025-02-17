from rest_framework import serializers
from .models import User



class UserSerializer(serializers.ModelSerializer):
    mot_de_passe = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "nom", "role", "mot_de_passe", "telephone"]
        extra_kwargs = {
            "role": {"required": False},  # Rôle optionnel, par défaut "PARTICIPANT"
        }

    def create(self, validated_data):
        mot_de_passe = validated_data.pop("mot_de_passe", None)
        user = User.objects.create_user(**validated_data)
        if mot_de_passe:
            user.set_password(mot_de_passe)
        user.save()
        return user
