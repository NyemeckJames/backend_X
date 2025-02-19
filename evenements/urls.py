from django.urls import path
from .views import CreerEvenementView, EvenementListView, UserEvenementsList, evenements_par_organisateur

urlpatterns = [
    path('create/', CreerEvenementView.as_view(), name='creer_evenement'),
    path('get_all/', EvenementListView.as_view(), name='liste_des_evenements'),
    path('my-events/', UserEvenementsList.as_view(), name='liste_de_mes_evenements'),
    path('mes-evenements/<int:orgid>', evenements_par_organisateur, name='mes-evenements'),
    path('mes-evenements/<int:orgid>/', evenements_par_organisateur, name='mes-evenements'),

]