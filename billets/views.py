from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Billet, Evenement
from .serializers import BilletSerializer

class CreerBilletView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Seuls les utilisateurs authentifiés peuvent créer un billet

    def post(self, request):
        """Créer un billet pour un événement donné, uniquement si l'utilisateur est authentifié."""

        # Récupérer les données du request
        evenement_id = request.data.get('evenement_id')
        type_billet = request.data.get('type_billet', Billet.Type.GRATUIT)  # Par défaut, gratuit
        prix = request.data.get('prix', 0.00)

        # Vérifier si l'événement existe
        try:
            evenement = Evenement.objects.get(id=evenement_id)
        except Evenement.DoesNotExist:
            return Response({"detail": "Événement non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        # Créer un billet pour l'utilisateur authentifié et l'événement
        billet = Billet.objects.create(
            evenement=evenement,
            participant=request.user,  # L'utilisateur connecté est le participant
            type_billet=type_billet,
            prix=prix
        )

        # Sérialisation du billet
        serializer = BilletSerializer(billet)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
