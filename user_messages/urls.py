from django.urls import path
from .views import SoumettreDemandeOrganisateurView, ListeDemandesEnAttenteView, GérerDemandeOrganisateurView

urlpatterns = [
    path("devenir-organisateur/", SoumettreDemandeOrganisateurView.as_view(), name="demande-organisateur"),
    path("admin/demandes-en-attente/", ListeDemandesEnAttenteView.as_view(), name="demandes-en-attente"),
    path("admin/gerer-demande/<int:user_id>/", GérerDemandeOrganisateurView.as_view(), name="gerer-demande"),
]
