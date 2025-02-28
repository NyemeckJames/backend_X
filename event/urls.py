from django.urls import path
from .views import CreateEventAPIView, GetAllEvents

urlpatterns = [
    path('create/', CreateEventAPIView.as_view(), name='creer_evenement'),
    path('events/', GetAllEvents.as_view(), name='get_all_event'),
]