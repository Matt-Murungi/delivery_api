from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.admin import AdminSite
from django.contrib import admin
from django import forms

from .models import User, Profile


class UserCreationForm(forms.ModelForm):
    """
    form for creating users
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    form for updating users
    """

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phonenumber")


class CustomUserAdmin(BaseUserAdmin):
    """
    user admin page
    """

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("email", "first_name", "last_name", "is_driver")
    list_filter = ("is_admin", "is_driver", "partner")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Personal info",
            {
                "fields": (
                    "is_driver",
                    "phonenumber",
                )
            },
        ),
        (
            "Partner",
            {"fields": ("partner",)},
        ),
        ("Permissions", {"fields": ("is_admin", "is_active", "is_confirmed")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = (
        "email",
        "phonenumber",
    )
    ordering = ("-date_joined",)
    filter_horizontal = ()


AdminSite.site_title = "bdeliv Admin"
AdminSite.site_header = "bdeliv Admin Panel"

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
admin.site.unregister(Group)
