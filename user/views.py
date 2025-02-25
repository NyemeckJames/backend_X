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
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
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
   
    
    