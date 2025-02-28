from django.db import models

# Create your models here.
import secrets
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.crypto import get_random_string


class UserManager(BaseUserManager):
    def create_user(self, email, nom, mot_de_passe=None, **extra_fields):
        """Créer et retourner un utilisateur avec une adresse e-mail et un mot de passe"""
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, **extra_fields)
        user.set_password(mot_de_passe)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, mot_de_passe=None, **extra_fields):
        """Créer et retourner un super-utilisateur"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, nom, prenom, mot_de_passe, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMINISTRATEUR", "Admin"
        ORGANISATEUR = "ORGANISATEUR", "Organisateur"
        PARTICIPANT = "PARTICIPANT", "Participant"
    class ValidationStatus(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        ACCEPTE = "ACCEPTE", "Accepté"
        REFUSE = "REFUSE", "Refusé"

    # L'ID sera généré aléatoirement sous forme de chaîne
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, null=True, blank=True, default="")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARTICIPANT)
    date_inscription = models.DateTimeField(auto_now_add=True)
    photo_profil = models.URLField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    email_verification_token = models.CharField(max_length=64, unique=True,blank=True, null=True)
    status_validation = models.CharField(
        max_length=20, choices=ValidationStatus.choices, default=ValidationStatus.EN_ATTENTE
    )
    nom_entreprise = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    numero_cni = models.CharField(max_length=50, blank=True, null=True)
    photo_cni = models.ImageField(upload_to="cni/", blank=True, null=True)
    types_evenements = models.JSONField(default=list, blank=True)
    taille_evenements = models.CharField(max_length=50, blank=True, null=True)
    mode_financement = models.CharField(max_length=50, blank=True, null=True)
    # Champs pour l'authentification
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  

    # Résolution du conflit en ajoutant un `related_name`
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.email})"
    def generate_email_verification_token(self):
        """Génère un token unique pour la vérification de l'email."""
        self.email_verification_token = get_random_string(64)
        self.save()
    def generate_password_reset_token(self):
        """Génère un token unique pour la réinitialisation du mot de passe."""
        self.password_reset_token = get_random_string(64)
        self.save()
