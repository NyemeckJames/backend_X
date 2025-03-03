from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from .models import DemandeOrganisateur
from .serializers import DemandeOrganisateurSerializer
from user.models import User
from rest_framework.generics import ListAPIView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
import json

class CreateDemandeOrganisateurView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Utiliser FormParser pour multipart/form-data

    def post(self, request):
        user = request.user
        print("user is : ", user)
        print("request.data : ", request.data)
        print("request.files : ", request.FILES)
        print("types_evenements: ", request.POST.getlist("types_evenements"))

        # Vérifier si une demande en attente existe déjà
        if DemandeOrganisateur.objects.filter(user=user, statut="EN_ATTENTE").exists():
            return JsonResponse(
                {"error": "Vous avez déjà une demande en attente."},
                status=400,
            )

        # Convertir types_evenements en liste
        types_evenements = request.POST.getlist("types_evenements")
        print("types_evenements après conversion :", types_evenements)

        # Créer une nouvelle demande sans utiliser de sérialiseur
        try:
            with transaction.atomic():  # Garantir une transaction sécurisée
                demande = DemandeOrganisateur.objects.create(
                    user=user,
                    nom_entreprise=request.POST.get("nom_entreprise"),
                    numero_cni=request.POST.get("numero_cni"),
                    facebook=request.POST.get("facebook", ""),
                    twitter=request.POST.get("twitter", ""),
                    types_evenements=types_evenements,  # Sauvegarder comme JSONField
                    taille_evenements=request.POST.get("taille_evenements"),
                    mode_financement=request.POST.get("mode_financement"),
                    photo_cni=request.FILES.get("photo_cni"),  # Sauvegarder l'image si fournie
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Demande soumise avec succès.",
                    "demande_id": demande.id,
                },
                status=201,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


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
        self.notify_user(demande.user, statut, commentaire)
        return Response({"message": f"Demande {statut.lower()} avec succès."}, status=status.HTTP_200_OK)
    def notify_user(self, user, decision, commentaire):
        subject = f"Votre demande pour devenir organisateur a été {decision.lower()}"
        message = render_to_string("emails/organizer_decision.html", {
            "user": user,
            "decision": decision,
            "commentaire": commentaire,
        })
        send_mail(
            subject,
            message,
            "jamesnyemeck@gmail.com",
            [user.email],
            html_message=message,
        )   
    

class ListeDemandesEnAttenteView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DemandeOrganisateurSerializer

    def get_queryset(self):
        return DemandeOrganisateur.objects.filter(statut="EN_ATTENTE").order_by("-date_demande")
    
class ListOrganizerRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        demandes = DemandeOrganisateur.objects.filter(statut="EN_ATTENTE")
        serializer = DemandeOrganisateurSerializer(demandes, many=True)
        return JsonResponse(serializer.data, safe=False)

class ReviewOrganizerRequestView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, demande_id):
        demande = DemandeOrganisateur.objects.get(id=demande_id)
        decision = request.data.get("decision")  # "ACCEPTE" ou "REFUSE"
        commentaire = request.data.get("commentaire", "")

        if decision not in ["ACCEPTE", "REFUSE"]:
            return JsonResponse({"error": "Décision invalide."}, status=400)

        demande.statut = decision
        demande.commentaire_admin = commentaire
        demande.save()

        # Notifier l'utilisateur
        self.notify_user(demande.user, decision, commentaire)

        return JsonResponse({"success": True, "message": f"Demande {decision.lower()}."})

    def notify_user(self, user, decision, commentaire):
        subject = f"Votre demande pour devenir organisateur a été {decision.lower()}"
        message = render_to_string("emails/organizer_decision.html", {
            "user": user,
            "decision": decision,
            "commentaire": commentaire,
        })
        send_mail(
            subject,
            message,
            "noreply@votredomaine.com",
            [user.email],
            html_message=message,
        )   
        
        