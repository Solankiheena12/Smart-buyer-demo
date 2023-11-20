from django.contrib.auth.models import Permission
from rest_framework import serializers

from user.models import ContentTypeModel, CustomGroup, User


class CustomGroupSerializers(serializers.ModelSerializer):
    sequence = serializers.IntegerField(source="customgroup.sequence", read_only=True)

    class Meta:
        model = CustomGroup
        fields = [
            "id",
            "name",
            "sequence",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class ContentTypeSerializers(serializers.ModelSerializer):
    permission_on = serializers.CharField(source="model")

    class Meta:
        model = ContentTypeModel
        fields = ["id", "permission_on"]


class PermissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]


class VerifyAccountSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "otp"]

    def validate(self, data):
        email = data["email"]
        query = User.objects.filter(email=email).first()
        if data["otp"] != str(query.otp):
            raise serializers.ValidationError("OTP is incorrect")
        return data


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "email",
            "otp",
        ]

    def validate(self, data):
        email = data["email"]
        query = User.objects.get(email=email)
        if data["otp"] != str(query.otp):
            raise serializers.ValidationError("OTP is incorrect")
        return data


class LoginWithEmailOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True)
    otp_method = serializers.CharField(required=True)
    whatsapp_verified = serializers.BooleanField()
    phone = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["email", "phone", "otp_method", "whatsapp_verified"]


class VerifyLoginWithEmailOtpSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, allow_null=True)
    phone = serializers.IntegerField(required=False, allow_null=True)
    otp = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ["email", "phone", "otp"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "phone"]
