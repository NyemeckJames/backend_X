from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import Message, Room

def get_messages(request, event_id):
    try:
        room = Room.objects.get(evenement_id=event_id)
        messages = Message.objects.filter(room=room).order_by("timestamp")
        data = [
            {"sender": msg.sender.nom, "message": msg.message, "timestamp": msg.timestamp}
            for msg in messages
        ]
        return JsonResponse({"messages": data})
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)
