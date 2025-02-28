from django.core.mail import send_mail
from django.conf import settings
import secrets
from .models import User

def send_verification_email(user):
    """Génère un token et envoie un email de confirmation"""
    verification_token = secrets.token_urlsafe(32)  # Générer un token sécurisé
    user.verification_token = verification_token
    user.save()

    verification_url = f"http://localhost:3000/verify-email?token={verification_token}"  # Remplace par ton URL frontend

    subject = "Vérification de votre email"
    message = f"Bonjour {user.nom},\n\nCliquez sur le lien suivant pour vérifier votre email : {verification_url}\n\nMerci !"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
