from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings
import os
from uuid import uuid4
from django.utils.html import mark_safe

# Custom User Manager
class CustomAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('Role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

# Custom User Model
class Users(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('user', 'Student'),
    )

    Role = models.CharField(max_length=20, choices=ROLES, default='user')
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# Section Model
class Section(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# Subject Model
class Subject(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name

# StudentSubject (Subjects assigned to students)
class StudentSubject(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'Role': 'user'},
        related_name='assigned_subjects'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    custom_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.username} - {self.custom_name or self.subject.subject_name}"

# TeacherSubject (Subjects offered by teachers)
class TeacherSubject(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'Role': 'teacher'}
    )
    subject_time = models.TimeField()

    def __str__(self):
        return f"{self.subject.subject_name} - {self.section.name} ({self.teacher.username})"

# Attendance Model
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'Role': 'user'}
    )
    subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='taken_attendance'
    )

    class Meta:
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.subject} - {self.date} - {self.status}"

# User Profile
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
    profile_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def profile_image_tag(self):
        if self.profile_image:
            return mark_safe(
                f'<img src="{self.profile_image.url}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />'
            )
        return "Image not available"

    profile_image_tag.short_description = 'Image'
