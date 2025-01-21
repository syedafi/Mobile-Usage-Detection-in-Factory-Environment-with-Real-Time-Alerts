
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone_number', 'organization', 'is_verified')  # Remove 'created_at'
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

# Register the updated UserAdmin
admin.site.register(User, UserAdmin)

# Register OTPVerification if needed
@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at')  # 'created_at' is valid here
    search_fields = ('email',) 