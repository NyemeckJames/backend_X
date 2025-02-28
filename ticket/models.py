from django.db import models
from django.core.validators import MinValueValidator
from user.models import User
from event.models import Event, Ticket
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class TicketPurchase(models.Model):
    STATUS_CHOICES = [
        ("valid", "Valide"),
        ("used", "Utilisé"),
        ("cancelled", "Annulé"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="purchases")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_purchases")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets_purchased")
    qr_code = models.ImageField(upload_to="tickets/qrcodes/", blank=True, null=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="valid")

    def __str__(self):
        return f"Billet {self.id} - {self.buyer.nom} {self.buyer.prenom} ({self.event.name})"

    def generate_qr_code(self):
        """ Génère un QR Code unique pour chaque billet """
        qr_data = f"ticket_id={self.id}&event_id={self.event.id}&buyer_id={self.buyer.id}"
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"ticket_{self.id}_qrcode.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:  # Générer un QR Code seulement si inexistant
            self.generate_qr_code()
        super().save(*args, **kwargs)
