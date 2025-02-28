from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from .models import DemandeOrganisateur
from .serializers import DemandeOrganisateurSerializer
from user.models import User
from rest_framework.generics import ListAPIView

class SoumettreDemandeOrganisateurView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Vérifier si l'utilisateur a déjà une demande en attente
        if DemandeOrganisateur.objects.filter(user=user).exists():
            return Response({"error": "Vous avez déjà une demande en attente."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DemandeOrganisateurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)  # Associer la demande à l'utilisateur
            return Response({"message": "Votre demande a été soumise avec succès."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GérerDemandeOrganisateurView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        try:
            demande = DemandeOrganisateur.objects.get(user_id=user_id)
        except DemandeOrganisateur.DoesNotExist:
            return Response({"error": "Demande introuvable"}, status=status.HTTP_404_NOT_FOUND)

        statut = request.data.get("statut")
        commentaire = request.data.get("commentaire_admin", "")

        if statut not in ["ACCEPTE", "REFUSE"]:
            return Response({"error": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)

        demande.statut = statut
        demande.commentaire_admin = commentaire
        demande.save()

        # Si accepté, mettre à jour le rôle utilisateur
        if statut == "ACCEPTE":
            user = demande.user
            user.role = User.Role.ORGANISATEUR
            user.save()

        return Response({"message": f"Demande {statut.lower()} avec succès."}, status=status.HTTP_200_OK)

class ListeDemandesEnAttenteView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DemandeOrganisateurSerializer

    def get_queryset(self):
        return DemandeOrganisateur.objects.filter(statut="EN_ATTENTE").order_by("-date_demande")