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
    

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Section
from .serializer import SectionSerializer

class SectionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # require auth, adjust as needed

    def get(self, request):
        sections = Section.objects.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # Optional
from .models import Subject
from .serializer import SubjectSerializer

class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]  # Remove this line if you want public access

    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

# views.py
from rest_framework import viewsets
from .models import StudentSubject
from .serializer import StudentSubjectSerializer

class StudentSubjectViewSet(viewsets.ModelViewSet):
    queryset = StudentSubject.objects.all()
    serializer_class = StudentSubjectSerializer
# views.py
from rest_framework import generics, permissions
from .models import TeacherSubject
from .serializer import TeacherSubjectSerializer

class TeacherSubjectListView(generics.ListAPIView):
    queryset = TeacherSubject.objects.select_related('subject', 'section', 'teacher').all()
    serializer_class = TeacherSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]  # Optional: allow only logged-in users
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Attendance
from .serializer import AttendanceSerializer

class TeacherOnlyMixin:
    permission_classes = [permissions.IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.user.Role != 'teacher':
            raise PermissionDenied("Only teachers are allowed.")

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Attendance, TeacherSubject, Section
from .serializer import AttendanceSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class AttendanceView(generics.GenericAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # List attendance records for sections/subjects assigned to this teacher
        queryset = Attendance.objects.filter(
            section__teachersubject__teacher=user
        ).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Expected a list of attendance records."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data, many=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Attendance recorded successfully."}, status=status.HTTP_201_CREATED)
