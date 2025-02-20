from django.urls import path
from .views import EnvoyerNotificationView, ListeNotificationsView

urlpatterns = [
    path('<int:evenement_id>/envoyer/', EnvoyerNotificationView.as_view(), name='envoyer-notification'),
    path('liste/', ListeNotificationsView.as_view(), name='liste-notifications'),
]
