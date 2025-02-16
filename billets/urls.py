from django.urls import path
from .views import CreerBilletView

urlpatterns = [
    path('create/', CreerBilletView.as_view(), name='creer_billet'),
]
