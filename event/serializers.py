from rest_framework import serializers
from .models import Event, Address, Speaker, Ticket, EventGallery

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class EventGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGallery
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    speakers = SpeakerSerializer(many=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    gallery = EventGallerySerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
