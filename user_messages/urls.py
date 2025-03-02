from django.urls import path
from .views import ListOrganizerRequestsView, GérerDemandeOrganisateurView, CreateDemandeOrganisateurView

urlpatterns = [
    path("devenir-organisateur/", CreateDemandeOrganisateurView.as_view(), name="demande-organisateur"),
    path("admin/demandes-en-attente/", ListOrganizerRequestsView.as_view(), name="demandes-en-attente"),
    path("admin/gerer-demande/<int:user_id>/", GérerDemandeOrganisateurView.as_view(), name="gerer-demande"),
]
