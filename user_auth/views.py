from sqlite3 import IntegrityError
from tokenize import TokenError
from jwt import InvalidTokenError
from rest_framework import status
#from .serializers import UserRegistrationSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from yaml import serialize

from core.models import Patient
from .serializers import HospitalUserSerializer #PatientProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
class RegisterStepOneAPIView(APIView):
    def post(self, request):
        serializer = HospitalUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)  # Generate a token for the newly created user
            return Response({
                "success": "User registered successfully.",
                "user_id": user.id,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


        
class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            patient = Patient.objects.get(user=user)
            patient_id = patient.id
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "patient_id": patient_id,
                'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


