from django.urls import path
from .views import CreateEventAPIView, GetAllEvents, GetEventByID

urlpatterns = [
    path('create/', CreateEventAPIView.as_view(), name='creer_evenement'),
    path('events/', GetAllEvents.as_view(), name='get_all_event'),
     path("events/<int:event_id>/", GetEventByID.as_view(), name="get-event-by-id"),
]