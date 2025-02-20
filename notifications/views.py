from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer
from evenements.models import Evenement
from user.models import User
from django.http import JsonResponse
from django.utils.timezone import now
from .models import Notification, Evenement, NotificationParticipant
from collections import defaultdict

class ListeNotificationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        participant = request.user

        # Récupérer toutes les notifications liées à ce participant
        notifications = NotificationParticipant.objects.filter(participant=participant).select_related("notification__evenement")

        # Agrégation par événement
        notifications_par_evenement = defaultdict(list)

        for notif_participant in notifications:
            evenement_id = notif_participant.notification.evenement.id
            serialized_notif = NotificationSerializer(notif_participant.notification).data
            notifications_par_evenement[evenement_id].append(serialized_notif)

        return JsonResponse(notifications_par_evenement, safe=False)

class EnvoyerNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request, evenement_id,):
        organisateur = request.user
        message = request.data.get("message")

        # Vérifier que l'événement existe et que l'utilisateur est bien son organisateur
        evenement = get_object_or_404(Evenement, id=evenement_id, organisateur=organisateur)

        if not message:
            return JsonResponse({"error": "Le message de la notification est requis."}, status=400)

        # Récupérer tous les participants qui ont un billet pour cet événement
        participants = User.objects.filter(billets__evenement=evenement).distinct()

        if not participants:
            return JsonResponse({"error": "Aucun participant trouvé pour cet événement."}, status=400)

        # Créer la notification principale
        notification = Notification.objects.create(
            evenement=evenement,
            organisateur=organisateur,
            message=message,
            date_envoi=now()
        )

        # Associer la notification à chaque participant
        notifications_participants = [
            NotificationParticipant(notification=notification, participant=participant) for participant in participants
        ]
        NotificationParticipant.objects.bulk_create(notifications_participants)

        return JsonResponse({"message": "Notification envoyée avec succès à tous les participants."}, status=201)

