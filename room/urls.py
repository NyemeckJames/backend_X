from django.urls import path
from .views import get_messages  # Remplace `my_view` par le bon import

urlpatterns = [
    path('get-all-room-messages/<int:event_id>', get_messages, name='get_chat_messages'),
]
