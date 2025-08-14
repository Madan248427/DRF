from datetime import timedelta
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from .serializer import RegistrationSerializer, CustomUserSerializer,UserUpdateSerializer

User = get_user_model()


# ----------------------------
# Custom Authentication Class
# ----------------------------
class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        try:
            validated_token = self.get_validated_token(token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            raise InvalidToken("Invalid access token in cookie")


# ----------------------
# Registration View
# ----------------------
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        user_data = CustomUserSerializer(user).data

        response = Response({"user": user_data}, status=status.HTTP_201_CREATED)
        response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='None', max_age=300, path='/')
        response.set_cookie('refresh_token', str(refresh), httponly=True, secure=True, samesite='None', max_age=7 * 24 * 3600, path='/')
        print("✅ [REGISTER] Access Token:", access_token[:30] + "...")
        print("✅ [REGISTER] Refresh Token:", str(refresh)[:30] + "...")
        return response


# ----------------------
# Login View
# ----------------------
class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data.pop('access', None)
        refresh_token = response.data.pop('refresh', None)

        if access_token:
            response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='None', max_age=300, path='/')
            print("✅ [LOGIN] Access Token:", access_token[:30] + "...")
        if refresh_token:
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='None', max_age=7 * 24 * 3600, path='/')
            print("✅ [LOGIN] Refresh Token:", refresh_token[:30] + "...")

        return response


# ----------------------
# Refresh View (from Cookie only)
# ----------------------
class RefreshFromCookie(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("📥 [REFRESH] POST /accounts/refresh/ called")

        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            print("❌ [REFRESH] No refresh token found in cookie.")
            return Response({'detail': 'No refresh token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_obj = RefreshToken(refresh_token)
            new_access = str(token_obj.access_token)
            print("🔁 [REFRESH] New access token:", new_access[:30] + "...")
        except InvalidToken:
            print("❌ [REFRESH] Invalid refresh token.")
            return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({'access': new_access}, status=status.HTTP_200_OK)
        response.set_cookie(
            'access_token',
            new_access,
            httponly=True,
            secure=True,  # Set to True in production
            samesite='None',
            max_age=300,
            path='/'
        )
        print("✅ [REFRESH] Token refreshed at", now())
        return response


# ----------------------
# Logout View
# ----------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthenticationFromCookie]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                print("🗑️ [LOGOUT] Refresh token blacklisted.")
            except Exception as e:
                print("⚠️ [LOGOUT] Error blacklisting token:", e)

        response = Response({"detail": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        print("✅ [LOGOUT] Cookies cleared.")
        return response


# ----------------------
# User Info View
# ----------------------
class UserDetail(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthenticationFromCookie]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        print(f"👤 [USER] Fetched user: {user.email}")
        return Response(serializer.data)
# views.py






User = get_user_model()

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthenticationFromCookie]

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
from .models import UserProfile
from .serializer import UserProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import UserProfile
from accounts.serializer import UserProfileSerializer
from rest_framework import status, permissions

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile  # OneToOneField related_name='profile'
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        # Create profile if doesn't exist
        try:
            request.user.profile
            return Response({"detail": "Profile already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            serializer = UserProfileSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Update profile if exists
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)