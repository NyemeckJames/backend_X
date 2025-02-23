from django.urls import path, re_path
from room.consumers import ChatConsumer
from notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    path("ws/messages/<int:event_id>/", ChatConsumer.as_asgi()),
    re_path(r"^ws/notifications/$", NotificationConsumer.as_asgi()),
]
