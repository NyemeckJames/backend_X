# serializers.py
from rest_framework import serializers
from .models import DemandeOrganisateur
import json
from rest_framework import serializers
from .models import DemandeOrganisateur, User
import json

class DemandeOrganisateurSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()  # ✅ Ajout du champ user_info

    class Meta:
        model = DemandeOrganisateur
        fields = [
            "id",
            "nom_entreprise",
            "facebook",
            "twitter",
            "numero_cni",
            "photo_cni",
            "types_evenements",
            "taille_evenements",
            "mode_financement",
            "statut",
            "date_demande",
            "commentaire_admin",
            "user_info",  # ✅ Ajout des infos utilisateur
        ]

    def get_user_info(self, obj):
        """Récupère les informations de l'utilisateur associé à la demande."""
        return {
            "user_id": obj.user.id,
            "nom": obj.user.nom,
            "prenom": obj.user.prenom,
            "email": obj.user.email,
            "telephone": obj.user.telephone,
        }

    def validate_types_evenements(self, value):
        """Validation et conversion du champ types_evenements."""
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("types_evenements doit être une liste valide.")
        
        if not isinstance(value, list):
            raise serializers.ValidationError("types_evenements doit être une liste.")

        return value
