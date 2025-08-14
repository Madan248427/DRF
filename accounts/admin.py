from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import mark_safe
from .models import Users, UserProfile

# Custom admin config for Users (custom user model)
class Userconfig(UserAdmin):
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

admin.site.register(Users, Userconfig)

# Admin config for UserProfile
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
            return mark_safe(f'<img src="{obj.profile_image.url}" width="80" height="80" style="object-fit: cover;" />')
        return "Image not available"

    profile_image_tag.short_description = "Profile Image"
