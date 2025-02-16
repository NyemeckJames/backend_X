from django.db import models

# Create your models here.
from django.db import models
from user.models import User
from evenements.models import Evenement  # Assurez-vous d'importer le modèle Evenement

class Billet(models.Model):
    class Type(models.TextChoices):
        GRATUIT = "GRATUIT", "Gratuit"
        PAYANT = "PAYANT", "Payant"

    # Identifiant unique du billet
    id = models.AutoField(primary_key=True)

    # Billet lié à un événement
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name="billets")

    # Billet lié à un utilisateur (participant)
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="billets"
    )

    # Informations sur le billet
    type_billet = models.CharField(max_length=20, choices=Type.choices, default=Type.GRATUIT)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_achat = models.DateTimeField(auto_now_add=True)
    code_qr = models.CharField(max_length=255, unique=True, blank=True, null=True)
    valide = models.BooleanField(default=False)

    # Statut du billet
    est_annule = models.BooleanField(default=False)

    def __str__(self):
        return f"Billet {self.id} pour l'événement {self.evenement.titre} - Participant {self.participant.nom} {self.participant.prenom}"

    def generer_code_qr(self):
        """
        Méthode pour générer un code QR pour ce billet.
        Utilise une bibliothèque externe pour générer un QR Code réel à partir du code du billet.
        """
        import qrcode
        import io
        from django.core.files.base import ContentFile

        # Code QR unique basé sur l'ID du billet
        qr_code_data = str(self.id)

        # Création du QR Code
        qr_code_image = qrcode.make(qr_code_data)
        buffer = io.BytesIO()
        qr_code_image.save(buffer)
        buffer.seek(0)

        # Sauvegarde de l'image QR dans un champ ImageField ou sous forme d'URL
        self.code_qr = f"qr_codes/{self.id}.png"
        self.save()

        # Optionnel : vous pouvez également stocker le QR code sous forme d'image
        # Par exemple, si vous utilisez AWS S3 ou un autre stockage, vous pouvez stocker ici l'URL du QR code.

        return self.code_qr

    class Meta:
        ordering = ['date_achat']
