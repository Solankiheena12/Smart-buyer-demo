from django.forms import ValidationError
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed

from user.models import User
from django.contrib.auth.models import Group, Permission


def get_user_permissions(user):
    user_permissions = Permission.objects.filter(user=user)
    custom_group_permissions = Permission.objects.filter(group__user=user)

    all_permissions_set = {
        f"{perm.content_type.app_label}|{perm.codename}" for perm in user_permissions
    } | {
        f"{perm.content_type.app_label}|{perm.codename}"
        for perm in custom_group_permissions
    }

    all_permissions = sorted(list(all_permissions_set))

    return all_permissions


def get_user_groups(user):
    groups = Group.objects.filter(user=user)
    group_data = [{"id": group.id, "name": group.name} for group in groups]
    return group_data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Get the provided login value (email or phone)
        login_value = attrs.get("email").lower()

        # Check if the provided input contains "@" (likely an email)
        if "@" in login_value and "." in login_value:
            user = User.objects.filter(email=login_value).first()

        else:
            # Assuming phone is unique, if not, adjust the query accordingly
            user = User.objects.filter(phone=login_value).first()

        if user is None:
            raise AuthenticationFailed(
                {
                    "success": False,
                    "message": "No active account found with the given credentials",
                }
            )

        
        attrs["email"] = user.email
        token = super(CustomTokenObtainPairSerializer, self).validate(attrs)

        permission_data = get_user_permissions(user)
        group_data = get_user_groups(user)

        token.update(
            {
                "userData": {
                    "user_id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                    "company": user.company_id,
                    "vendor": user.vendor_id,
                    "employee": user.employee_id,
                    "role": group_data,
                    "permission": permission_data,
                }
            }
        )

        user.last_login = now()
        user.save()

        data = {
            "success": True,
            "message": "Login Successful",
            "data": token,
        }

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get_auth_token(self, user):
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        return token
