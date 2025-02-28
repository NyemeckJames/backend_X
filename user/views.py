from django.shortcuts import get_object_or_404
from evenements.models import Evenement
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from billets.models import Billet
from .models import User
from django.core.mail import send_mail

from .serializers import UserSerializer

# Create your views here.
class LoginView(APIView):
    
    permission_classes = [AllowAny] 
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f"Les identifiants : {email},{password}")

        # Authentification de l'utilisateur
        user = authenticate(username=email, password=password)
        print("User is :",user)

        if user is not None:
            if not user.is_email_verified:
                return Response({"detail": "Veuillez vérifier votre adresse email avant de vous connecter."}, status=status.HTTP_403_FORBIDDEN)

            # Génération des tokens JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),  # Token d'accès
                'refresh': str(refresh),             # Token de rafraîchissement
                'user': {
                    'id': user.id,
                    'nom': user.nom,
                    'prenom': user.prenom,
                    'date_inscription': user.date_inscription,
                    'telephone': user.telephone,
                    'email': user.email,
                    'role': user.role,
                    
                }
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SignUpView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        print(request.data)
        data = request.data.copy()  # Crée une copie pour modifier les données
        data.pop("confirmPassword", None)  # Supprime confirmPassword s'il existe
        print("data : ", data)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.generate_email_verification_token()  # Génération du token

            # Envoi de l'email de confirmation
            verification_link = f"{settings.FRONTEND_URL}/verify-email?token={user.email_verification_token}"
            send_mail(
                "Vérifiez votre adresse email",
                f"Bonjour {user.nom},\n\nCliquez sur ce lien pour vérifier votre adresse email : {verification_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response(
                {
                    "message": "Inscription réussie.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "nom": user.nom,
                        "role": user.role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"error": "Token manquant"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email_verification_token=token)
            user.is_email_verified = True
            user.email_verification_token = None  # Supprimer le token après vérification
            user.save()
            return Response({"message": "Email vérifié avec succès."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            user.generate_password_reset_token()

            reset_link = f"{settings.FRONTEND_URL}/reset-password?token={user.password_reset_token}"
            send_mail(
                "Réinitialisation du mot de passe",
                f"Bonjour {user.nom},\n\nCliquez sur ce lien pour réinitialiser votre mot de passe : {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "Un email de réinitialisation a été envoyé."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Aucun utilisateur avec cet email"}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return Response({"error": "Token et nouveau mot de passe requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(password_reset_token=token)
            user.set_password(new_password)
            user.password_reset_token = None  # Supprimer le token après réinitialisation
            user.save()
            return Response({"message": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        evenement_id = data.get("evenement_id")
        prix = data.get("prix")  # En centimes (ex: 25000 XAF = 25000)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "xaf",
                            "product_data": {
                                "name": "Participation à l'événement",
                            },
                            "unit_amount": prix,  # Prix en centimes
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="http://localhost:3000/interfaces/participant/payment-sucess?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:3000/cancel",
                metadata={
                    "evenement_id": evenement_id,  # Ajout des métadonnées
                    "prix": prix
                }
            )
            return JsonResponse({"url": session.url})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=500)
        

class PaymentSuccess(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request,session_id, *args, **kwargs):
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)

        # Récupérer l'événement à partir des métadonnées
        evenement_id = session.metadata.get("evenement_id")
        prix = session.metadata.get("prix")
        evenement = get_object_or_404(Evenement, id=evenement_id)
        if evenement.billets_disponibles <= 0:
            return JsonResponse(
                {"error": "Plus de billets disponibles pour cet événement."},
                status=400
            )
        
        # Récupérer l'utilisateur connecté
        user = request.user
        billet_existant = Billet.objects.filter(evenement=evenement, participant=user).first()
        if not billet_existant:  # Si aucun billet n'existe, on en crée un
            billet = Billet.objects.create(
                evenement=evenement,
                participant=user,
                type_billet=Billet.Type.PAYANT,  # Puisque c'est payant
                prix=prix,  # Assumer que l'événement a un prix
            )
            # Décrémenter le nombre de billets disponibles
            evenement.billets_disponibles -= 1
            evenement.save()
        else:
            return JsonResponse({
                                    "titre": evenement.titre,
                                    "description": evenement.description,
                                    "lieu": evenement.lieu,
                                    "date": evenement.date_heure.strftime("%d/%m/%Y"),
                                    "billet_id": billet_existant.id,  # Retourner l'ID du billet dans la réponse
                                })
        # Créer un billet pour l'utilisateur
        

        # Retourner des informations sur l'événement et le billet
        return JsonResponse({
            "titre": evenement.titre,
            "description": evenement.description,
            "lieu": evenement.lieu,
            "date": evenement.date_heure.strftime("%d/%m/%Y"),
            "billet_id": billet.id,  # Ajouter l'ID du billet dans la réponse
        })

class RegisterEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id, *args, **kwargs):
        evenement = get_object_or_404(Evenement, id=event_id)
        user = request.user
        print("Utilisateur :", user)

        # Vérifier si des billets sont encore disponibles
        if evenement.billets_disponibles <= 0:
            return JsonResponse(
                {"error": "Plus de billets disponibles pour cet événement."},
                status=400
            )

        # Vérifier si l'événement est gratuit
        if evenement.evenementLibre:
            billet_existant = Billet.objects.filter(evenement=evenement, participant=user).first()
            print("Billet existant : ", billet_existant)
            
            if not billet_existant:
                # Créer le billet et décrémenter le nombre de billets disponibles
                billet = Billet.objects.create(
                    evenement=evenement,
                    participant=user,
                    type_billet=Billet.Type.GRATUIT,
                    prix=0.00,
                )

                # Décrémenter le nombre de billets disponibles
                evenement.billets_disponibles -= 1
                evenement.save()

                return JsonResponse({
                    "titre": evenement.titre,
                    "description": evenement.description,
                    "lieu": evenement.lieu,
                    "date": evenement.date_heure.strftime("%d/%m/%Y"),
                    "billet_id": billet.id,
                    "billets_restants": evenement.billets_disponibles,  # Info utile pour l'affichage
                })
            else:
                return JsonResponse({
                    "titre": evenement.titre,
                    "description": evenement.description,
                    "lieu": evenement.lieu,
                    "date": evenement.date_heure.strftime("%d/%m/%Y"),
                    "billet_id": billet_existant.id,
                    "billets_restants": evenement.billets_disponibles,
                })
        
        else:
            return JsonResponse({"error": "L'événement est payant, veuillez procéder au paiement."}, status=400)
class GetUserByID(APIView):
    def get(self, request, user_id, *args, **kwargs):
        user = User.objects.filter(id = user_id).first()
        if user:
            return JsonResponse({
                "name" : user.nom,
                "email" : user.email,
                "telephone": user.telephone
            })
        return JsonResponse({"error": "Utilisateur inexistant"}, status=404)
        

def get_all_users(request):
    if request.method == "GET":
        users = User.objects.all().values("id", "nom", "prenom", "email", "role")
        users_list = [
            {
                "id": str(user["id"]),
                "name": f"{user['nom']} {user['prenom']}".strip(),
                "email": user["email"],
                "role": "organizer" if user["role"] == "ORGANISATEUR" else "participant",
            }
            for user in users
        ]
        return JsonResponse({"users": users_list}, safe=False)
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
   
    
    