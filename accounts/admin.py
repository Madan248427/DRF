from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import mark_safe
from .models import (
    Users, UserProfile, Subject, StudentSubject, Section,
    TeacherSubject, Attendance
)

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    ordering = ['email']
    list_display = ('email', 'username', 'Role', 'is_superuser', 'is_staff', 'is_active')
    list_filter = ('Role', 'is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        ('Basic Info', {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('Role',)}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'Role'),
        }),
    )

admin.site.register(Users, CustomUserAdmin)

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'profile_image_tag',
        'phone_number',
        'location',
        'birth_date',
        'created_at',
    )
    readonly_fields = ('profile_image_tag',)
    search_fields = ('user__email', 'user__username', 'phone_number')
    list_filter = ('location', 'birth_date')

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return mark_safe(
                f'<img src="{obj.profile_image.url}" width="80" height="80" style="object-fit: cover; border-radius: 5px;" />'
            )
        return "Image not available"

    profile_image_tag.short_description = "Profile Image"

# Subject Admin
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_name')
    search_fields = ('subject_name',)

# StudentSubject Admin
@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'custom_name')
    search_fields = ('student__username', 'subject__subject_name')
    list_filter = ('subject', 'student')

# Section Admin
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# TeacherSubject Admin
@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'section', 'teacher', 'subject_time')
    list_filter = ('section', 'teacher')
    search_fields = ('subject__subject_name', 'teacher__username', 'section__name')
    autocomplete_fields = ('subject', 'section', 'teacher')

# Attendance Admin
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'section', 'date', 'status', 'taken_by')
    list_filter = ('status', 'date', 'section', 'subject')
    search_fields = ('student__username', 'taken_by__username', 'subject__subject_name', 'section__name')
    autocomplete_fields = ('student', 'subject', 'section', 'taken_by')
    date_hierarchy = 'date'
