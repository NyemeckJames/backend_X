from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from .models import Event, Address, Speaker, Ticket, EventGallery
import json
from .serializers import EventSerializer

import json
from collections import defaultdict
import re

def clean_request(request):
    cleaned_data = defaultdict(dict)
    cleaned_files = defaultdict(list)
    
    # Suppression des doublons dans les listes
    def remove_duplicates(value):
        return list(dict.fromkeys(value)) if isinstance(value, list) else value
    
    # Nettoyage des données textuelles
    for key, value in request.data.lists():
        if key.startswith("speakers") or key.startswith("tags"):
            cleaned_data[key] = remove_duplicates(value)
        elif key.startswith("adress") and key.endswith("location"):
            try:
                cleaned_data[key] = json.loads(value[0])  # Parser correctement les JSON
            except json.JSONDecodeError:
                print(f"[Erreur] Impossible de parser {key} : {value[0]}")
                cleaned_data[key] = None
        elif key == "ticketCloseDate" and not value[0]:
            cleaned_data[key] = None  # Rendre null si vide
        else:
            cleaned_data[key] = value[0] if len(value) == 1 else value
    
    # Vérification des dates
    ticket_open = cleaned_data.get("ticketOpenDate")
    start_date = cleaned_data.get("startDateTime")
    if ticket_open and start_date and ticket_open > start_date:
        print(f"[Erreur] ticketOpenDate ({ticket_open}) est postérieur à startDateTime ({start_date})")
        cleaned_data["ticketOpenDate"] = None
    
    # Vérification de la capacité vs nombre de billets
    total_tickets = sum(int(cleaned_data[key]) for key in cleaned_data if "tickets" in key and key.endswith("quantity"))
    event_capacity = int(cleaned_data.get("capacity", 0))
    if total_tickets > event_capacity:
        print(f"[Erreur] Nombre total de billets ({total_tickets}) dépasse la capacité ({event_capacity})")
        cleaned_data["capacity"] = total_tickets  # Mise à jour de la capacité
    
    # Nettoyage des fichiers
    for key, file_list in request.FILES.lists():
        unique_files = []
        seen_files = set()
        for file in file_list:
            if file.name not in seen_files:
                seen_files.add(file.name)
                unique_files.append(file)
        cleaned_files[key] = unique_files if len(unique_files) > 1 else unique_files[0]
    
    cleaned_request = {"data": dict(cleaned_data), "files": dict(cleaned_files)}
    
    return cleaned_request

def str_to_bool(value:str):
    return value.lower() == 'true'

def extract_speakers(data):
    speakers = []
    speaker_pattern = re.compile(r"speakers\[(\d+)\]\[(\w+)\]")

    speaker_dict = {}
    for key, value in data.items():
        match = speaker_pattern.match(key)
        if match:
            index, field = int(match.group(1)), match.group(2)
            if index not in speaker_dict:
                speaker_dict[index] = {}
            if field == "photo":
                # Filtrer et garder uniquement l'objet TemporaryUploadedFile
                speaker_dict[index][field] = next((v for v in value if hasattr(v, "file")), None)
            else:
                speaker_dict[index][field] = value[0] if isinstance(value, list) else value

    for index in sorted(speaker_dict.keys()):
        speakers.append(speaker_dict[index])

    return speakers

def extract_addresses(data):
    addresses = []
    address_pattern = re.compile(r"adress\[(\d+)\]\[(\w+)\]")

    address_dict = {}
    for key, value in data.items():
        match = address_pattern.match(key)
        if match:
            index, field = int(match.group(1)), match.group(2)
            if index not in address_dict:
                address_dict[index] = {}
            if field == "location":
                # Convertir la chaîne JSON en dictionnaire
                address_dict[index][field] = json.loads(value)
            else:
                address_dict[index][field] = value

    for index in sorted(address_dict.keys()):
        addresses.append(address_dict[index])

    return addresses

def extract_tickets(data):
    tickets = []
    ticket_pattern = re.compile(r"tickets\[(\d+)\]\[(\w+)\]")

    ticket_dict = {}
    for key, value in data.items():
        match = ticket_pattern.match(key)
        if match:
            index, field = int(match.group(1)), match.group(2)
            if index not in ticket_dict:
                ticket_dict[index] = {}
            ticket_dict[index][field] = value

    for index in sorted(ticket_dict.keys()):
        ticket = ticket_dict[index]
        ticket["price"] = float(ticket["price"])  # Conversion en float
        ticket["quantity"] = int(ticket["quantity"])  # Conversion en int
        tickets.append(ticket)

    return tickets

def extract_gallery(data):
    gallery = set()  # Utilisation d'un set pour éviter les doublons
    gallery_pattern = re.compile(r"gallery\[\d+\]\[\d+\]")

    for key, value in data.items():
        if gallery_pattern.match(key) and hasattr(value, "file"):  
            gallery.add(value)  # Ajoute uniquement les TemporaryUploadedFile

    return list(gallery)  # Conversion en liste pour la compatibilité

def extract_tags(data):
    tags = []
    tags_pattern = re.compile(r"tags\[\d+\]")  # Détecte les clés tags[x]

    for key, value in data.items():
        if tags_pattern.match(key) and isinstance(value, list):  
            tags.extend(value)  # Ajoute tous les tags extraits

    return tags  # Retourne une liste de tags sous un format JSONField-compatible


class CreateEventAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        cleaned_request = clean_request(request)
        data = cleaned_request.get("data")
        files = cleaned_request.get("files")
        print("data : ", data)
        promo_video = data.get("promoVideo")  
        
        tickets = extract_tickets(data)
        gallery = extract_gallery(files)
        addresses = extract_addresses(data)
        speakers = extract_speakers(data)
        tags = extract_tags(data)
        try:
            # Créer l'événement
            event = Event.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                category=data['category'],
                start_datetime=data['startDateTime'],
                end_datetime=data['endDateTime'] if data.get('endDateTime') else None,
                country=data.get('country', ''),
                online_link=data.get('onlineLink', ''),
                capacity=int(data['capacity']),
                ticket_open_date=data['ticketOpenDate'],
                ticket_close_date=data['ticketCloseDate'] if data.get('ticketCloseDate') else None,
                organizer_name=data['organizerName'],
                organizer_contact=data['organizerContact'],
                promo_video = promo_video,
                organizer_website=data['organizerWebsite'],
                confirmation_email=data.get('confirmationEmail', ''),
                reminder_messages=str_to_bool(data.get('reminderMessages', 'false')),
                qr_code=str_to_bool(data.get('qrCode', 'false')),
                access_control=str_to_bool(data.get('accessControl', 'false')),
                moderation=str_to_bool(data.get('moderation', 'false')),
                tags = tags
            )
            event.generate_qr_code()
            
            # Ajouter l'image de couverture
            if 'coverImage' in files:
                event.cover_image = files['coverImage']
                event.save()
                

            # Ajouter les billets
            for ticket_data in tickets:
                print("name : ", ticket_data['name'])
                ticket = Ticket.objects.create(
                    event=event,
                    name=ticket_data['name'],
                    price=ticket_data['price'],
                    quantity=ticket_data['quantity']
                )
                event.tickets.add(ticket)

            # Ajouter les adresses
            for address_data in addresses:
                location = address_data['location']
                address = Address.objects.create(
                    name=address_data.get('name', ''),
                    location_title=address_data['location_title'],
                    latitude=location.get('latitude'),
                    longitude=location.get('longitude'),
                    additional_contact_name=address_data.get('additional_contact_name', ''),
                    additional_contact_phone=address_data.get('additional_contact_phone', ''),
                    delivery_track_id=address_data.get('delivery_track_id', ''),
                )
                event.addresses.add(address)

            # Ajouter les intervenants
            for speaker_data in speakers:
                speaker = Speaker.objects.create(
                    name=speaker_data['name'],
                    occupation=speaker_data.get('occupation', ''),
                    facebook=speaker_data.get('facebook', ''),
                    linkedin=speaker_data.get('linkedin', ''),
                )
                if 'photo' in speaker_data:
                    speaker.photo = speaker_data['photo']
                    speaker.save()
                event.speakers.add(speaker)

            # Ajouter la galerie
            for file in gallery:
                gallery_image = EventGallery.objects.create(event=event, image=file)
                gallery_image.save()


            """# Ajouter la vidéo promo
            if 'promoVideo' in files:
                event.promo_video = files['promoVideo']
                event.save()"""

            event.save()  # Sauvegarder après avoir ajouté toutes les données liées

            return Response({"message": "Event created successfully", "event_id": event.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetAllEvents(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class GetEventByID(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"error": "Événement introuvable"}, status=status.HTTP_404_NOT_FOUND)



       
    
