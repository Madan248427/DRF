from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # 🔐 Auth & User
    RegisterView,
    CookieTokenObtainPairView,
    RefreshFromCookie,
    LogoutView,
    UserDetail,
    UserUpdateView,
    UserProfileView,
    SubjectListView,
    TeacherSubjectListView,
    AttendanceView,
    # 📚 Section API
    SectionListView,

    # 📘 StudentSubject API
    StudentSubjectViewSet,
)

# DRF router for ViewSets
router = DefaultRouter()
router.register(r'student-subjects', StudentSubjectViewSet, basename='student-subject')

urlpatterns = [
    # 🔐 Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('refresh/', RefreshFromCookie.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # 👤 User
    path('user/', UserDetail.as_view(), name='user-detail'),
    path('profile/update/', UserUpdateView.as_view(), name='profile-update'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # 📚 Section & Subject
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('sections/', SectionListView.as_view(), name='section-list'),
    path('teacher-subjects/', TeacherSubjectListView.as_view(), name='teacher-subjects-list'),
    # 📘 StudentSubject API
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('', include(router.urls)),  # Include ViewSet routes
]
