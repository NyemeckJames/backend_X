from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response

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
