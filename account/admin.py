from django.contrib import admin
from .models import User, Service, InformReport, Payment
from .forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = (
        "phone_number", "first_name", "last_name", "is_staff")
    list_filter = (
        "is_staff", "is_superuser", "is_active", "subscription", "groups")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": (
            "first_name", "last_name", "phone_number")}),
        ("Permissions", {"fields": (
            "is_active", "is_staff", "is_superuser", "subscription", "sub_type", "groups", "user_permissions")}),
        ("Important Dates", {"fields": (
            "last_login", "sub_expire_date")})
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "phone_number", "password1", "password2"
            )}),
    )
    search_fields = ("email", "phone_number")
    ordering = ("phone_number", "email")


admin.site.register(User, UserAdmin)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'datetime', 'checking_url', 'expired']
    list_filter = ["expired"]


@admin.register(InformReport)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'datetime']
    list_filter = ["status"]


@admin.register(Payment)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'datetime', 'description', 'status']
    list_filter = ["datetime"]

