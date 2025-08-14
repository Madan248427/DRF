from django.urls import path
from .views import (
    RegisterView,
    CookieTokenObtainPairView,
    RefreshFromCookie,
    LogoutView,
    UserDetail,
    UserUpdateView,
    UserProfileView,  # <-- Import the new view
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('refresh/', RefreshFromCookie.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserDetail.as_view(), name='user-detail'),
    path('profile/update/', UserUpdateView.as_view(), name='profile-update'),  # For user email/username/pass
    path('profile/', UserProfileView.as_view(), name='user-profile'),  # <-- NEW: for profile data + image
]
