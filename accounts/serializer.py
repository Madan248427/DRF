from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# ✅ 1. User Serializer (for return data) - FIXED to include Role
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'Role']  # Added Role field

# ✅ 2. Registration Serializer - FIXED to handle Role
class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    Role = serializers.ChoiceField(choices=User.ROLES, default='user')  # Added Role field
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password1', 'password2', 'Role']

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match")
        if len(attrs['password1']) < 4:
            raise serializers.ValidationError("Password should have at least 4 characters")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        # Make sure Role is included in user creation
        user = User.objects.create_user(password=password, **validated_data)
        return user

# ✅ 3. Login Serializer - No changes needed
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required")
        
        user = authenticate(username=email, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect credentials")
    

# serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=4)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance

# serializer.py

from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['bio', 'birth_date', 'location', 'phone_number', 'profile_image', 'profile_image_url']

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def create(self, validated_data):
        user = self.context['request'].user
        return UserProfile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
from rest_framework import serializers
from .models import Section, TeacherSubject, Users, Attendance, StudentSubject, UserProfile

# Simple Section Serializer
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']

# TeacherSubject Serializer with nested subject name
class TeacherSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)

    class Meta:
        model = TeacherSubject
        fields = ['id', 'subject_name', 'section', 'subject_time']

# Student Serializer with basic fields and section info from UserProfile
class StudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email']

# Attendance Serializer for POST and GET attendance records
# serializers.py
from rest_framework import serializers
from .models import Section

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']

from rest_framework import serializers
from .models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subject_name']
# serializers.py
from rest_framework import serializers
from .models import StudentSubject

class StudentSubjectSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)

    class Meta:
        model = StudentSubject
        fields = ['id', 'student', 'student_username', 'subject', 'subject_name', 'custom_name']
# serializers.py
from rest_framework import serializers
from .models import TeacherSubject

class TeacherSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.subject_name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.username", read_only=True)

    class Meta:
        model = TeacherSubject
        fields = ['id', 'subject', 'subject_name', 'section', 'section_name', 'teacher', 'teacher_name', 'subject_time']
from rest_framework import serializers
from .models import Attendance

from rest_framework import serializers
from .models import Attendance, TeacherSubject, Section
from django.contrib.auth import get_user_model

User = get_user_model()

class AttendanceSerializer(serializers.ModelSerializer):
    # For read, expand related fields; for write, accept IDs
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(Role='user'))
    subject = serializers.PrimaryKeyRelatedField(queryset=TeacherSubject.objects.all())
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    status = serializers.ChoiceField(choices=Attendance.STATUS_CHOICES)
    date = serializers.DateField()

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'subject', 'section', 'date', 'status', 'taken_by']
        read_only_fields = ['taken_by']

    def validate(self, data):
        user = self.context['request'].user

        # Validate that the teacher is assigned to the section and subject
        subject = data['subject']
        section = data['section']
        if subject.teacher != user:
            raise serializers.ValidationError("You are not assigned to this subject.")
        if subject.section != section:
            raise serializers.ValidationError("Subject does not belong to the specified section.")

        # Additional validation can be added here as needed

        return data

    def create(self, validated_data):
        # Prevent duplicate attendance (unique_together enforced by model)
        attendance_obj, created = Attendance.objects.update_or_create(
            student=validated_data['student'],
            subject=validated_data['subject'],
            date=validated_data['date'],
            defaults={
                'section': validated_data['section'],
                'status': validated_data['status'],
                'taken_by': self.context['request'].user,
            }
        )
        return attendance_obj