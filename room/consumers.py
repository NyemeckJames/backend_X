import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message, User

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room_name = f"event_{self.event_id}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        self.close(code)

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        
        # Récupération des données envoyées par le client
        event_id = data_json["event_id"]
        sender_id = data_json["sender_id"]
        message_text = data_json["message"]
        print(f"event_id : ${event_id} sender_id : ${sender_id} message_text : ${message_text}")

        event = {"type": "send_message", "message": data_json}
        await self.channel_layer.group_send(self.room_name, event)

    async def send_message(self, event):
        data = event["message"]
        # Récupère l'utilisateur correspondant au sender_id
        sender_id = sender_id = data["sender_id"]
        sender = await self.get_user(sender_id)
        await self.create_message(data=data)

        response = {
            "sender": sender.nom,
            "message": data["message"],
        }

        await self.send(text_data=json.dumps({"message": response}))

    @database_sync_to_async
    def create_message(self, data):
        room = Room.objects.get(evenement_id=data["event_id"])
        sender = User.objects.get(id=data["sender_id"])

        Message.objects.create(room=room, sender=sender, message=data["message"])
    
    @database_sync_to_async
    def get_user(self, sender_id):
        # Récupère l'utilisateur depuis la base de données
        return User.objects.get(id=sender_id)
