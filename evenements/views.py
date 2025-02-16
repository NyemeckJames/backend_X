from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Evenement
from .serializers import EvenementSerializer

class CreerEvenementView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Seuls les utilisateurs authentifiés peuvent accéder

    def post(self, request):
        """Créer un événement uniquement si l'utilisateur est ORGANISATEUR ou ADMIN."""
        user = request.user

        # Vérifier si l'utilisateur est un ORGANISATEUR ou ADMIN
        if user.role not in [User.Role.ADMIN, User.Role.ORGANISATEUR]:
            return Response(
                {"detail": "Permission refusée. Seuls les organisateurs et admins peuvent créer un événement."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Ajouter automatiquement l'utilisateur comme organisateur
        data = request.data.copy()
        data["organisateur"] = user.id  # Associer l'événement à l'utilisateur connecté

        # Sérialisation des données et validation
        serializer = EvenementSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EvenementListView(APIView):
    permission_classes = [AllowAny]
    """
    Vue pour récupérer la liste de tous les événements existants dans la base de données.
    """
    def get(self, request, *args, **kwargs):
        # Récupérer tous les événements de la base de données
        evenements = Evenement.objects.all()

        # Sérialiser les événements
        serializer = EvenementSerializer(evenements, many=True)

        # Retourner la réponse JSON
        return Response(serializer.data, status=status.HTTP_200_OK)