from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator
from user.models import User
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Address(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    location_title = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    additional_contact_name = models.CharField(max_length=255, null=True, blank=True)
    additional_contact_phone = models.CharField(max_length=20, null=True, blank=True)
    delivery_track_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name or self.location_title or "Adresse inconnue"


class Speaker(models.Model):
    name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    photo = models.ImageField(upload_to="speakers/photos/", null=True, blank=True)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="event_tickets") 
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Le prix ne peut pas être negatif"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Au moins 1 billet doit être disponible")

    def __str__(self):
        return f"{self.name} - {self.event.name}"


class Event(models.Model):
    CATEGORY_CHOICES = [
        ("Concert", "Concert"),
        ("Conférence", "Conférence"),
        ("Festival", "Festival"),
        ("Atelier", "Atelier"),
        ("Autre", "Autre"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    start_datetime = models.TextField()
    end_datetime = models.TextField(null=True, blank=True)
    timezone = models.CharField(max_length=100, null=True, blank=True)
    qr_code_image = models.ImageField(upload_to="events/qrcodes/", blank=True, null=True)
    addresses = models.ManyToManyField(Address, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    online_link = models.URLField(null=True, blank=True)

    capacity = models.PositiveIntegerField()
    ticket_open_date = models.TextField(null=True, blank=True)
    ticket_close_date = models.TextField(null=True, blank=True)

    organizer_name = models.CharField(max_length=255)
    organizer_contact = models.EmailField()
    organizer_website = models.URLField(null=True, blank=True)

    cover_image = models.ImageField(
        upload_to="events/covers/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
        null=True, blank=True
    )
    gallery = models.ManyToManyField("EventGallery", blank=True, related_name="events")
    promo_video = models.FileField(
        upload_to="events/videos/",
        validators=[FileExtensionValidator(allowed_extensions=["mp4", "mov", "avi"])],
        null=True,
        blank=True,
    )
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events_organized", null=True, blank=True)
    speakers = models.ManyToManyField(Speaker, blank=True)
    tags = models.JSONField(default=list, blank=True,null=True)
    tickets = models.ManyToManyField(Ticket, blank=True, related_name="event_tickets")
    confirmation_email = models.TextField(null=True, blank=True)
    reminder_messages = models.BooleanField(default=False)
    qr_code = models.BooleanField(default=False)
    access_control = models.BooleanField(default=False)
    moderation = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def generate_qr_code(self):
        """ Génère un QR Code basé sur l'ID de l'événement et l'URL associée """
        qr = qrcode.make(f"http://localhost:3000/event/{self.id}")  # Lien de l'événement
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        
        self.qr_code_image.save(f"event_{self.id}_qrcode.png", ContentFile(buffer.getvalue()), save=False)
        
   
class EventGallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_images")
    image = models.ImageField(
        upload_to="events/gallery/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
    )

    def __str__(self):
        return f"Image for {self.event.name}"




