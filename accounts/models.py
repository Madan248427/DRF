from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class CustomAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **args):
        if not email:
            raise ValueError("Must provide email")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **args)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **kwargs):
        kwargs.setdefault('Role', 'admin')
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **kwargs)

class Users(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('teacher', 'Teacher'),
    )

    Role = models.CharField(choices=ROLES, default='user',max_length=20)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if self.Role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    # ✅ Add these two methods to fix get_full_name error
    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
from django.db import models
from django.conf import settings
from django.utils import timezone
import os
from uuid import uuid4

# Helper for unique file path per user
def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join('user_images', str(instance.user.id), filename)

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_image = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

    def profile_image_tag(self):
        if self.profile_image:
            return f'<img src="{self.profile_image.url}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />'
        return "Image not available"
    profile_image_tag.short_description = 'Image'
    profile_image_tag.allow_tags = True  # For older Django versions (not required in Django 3.0+)
