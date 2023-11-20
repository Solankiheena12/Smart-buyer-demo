import json
import threading

from django.utils.timezone import now
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
# from company.models import Company
from email_utils.send_inactive_email import send_inactive_email

# from employee.models import Employee
from user.models import User
from user.serializers import (
    LoginWithEmailOtpSerializer,
    VerifyLoginWithEmailOtpSerializer,
    VerifyOTPSerializer,
)
from user.user_auth import (
    CustomTokenObtainPairSerializer,
    CustomTokenObtainPairView,
    get_user_groups,
    get_user_permissions,
)
from utils.generate_otp import generate_otp, send_otp_email
from email_utils.send_email import decode_token, generate_token, send_mail
from email_utils.send_success_mail import send_confirm_mail, send_success_mail
# from vendor.models import Vendor


class VerifyOtpViewSet(ModelViewSet):
    serializer_class = VerifyOTPSerializer
    queryset = User.objects.all().order_by("-id")

    def create(self, request, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data, partial=True)
        if serializer.is_valid():
            email = data.get("email")
            otp = data.get("otp")
            user = User.objects.filter(email=email).first()
            if user is None:
                return Response(
                    {"success": False, "message": "User not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if user.otp == otp:
                user.is_active = True
                user.status = "active"
                user.otp = None
                user.save()
                return Response(
                    {
                        "success": True,
                        "message": "OTP verification successful. You are registered.",
                    }
                )
            else:
                return Response(
                    {"success": False, "message": "Invalid OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"success": False, "message": "No Email Address Found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.is_active:
            return Response(
                {"success": False, "message": "User not active with us"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = generate_token(email, 60)
        name = user.first_name
        context = {"name": name, "token": token, "email": email}
        current_site = request._current_scheme_host + request.path
        context["current_site"] = current_site
        send_mail("Reset Your Password", "reset-pass.html", context)
        return Response(
            {"success": True, "message": "Mail has been sent to registed email"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all().order_by("-id")

    def create(self, request, token, *args, **kwargs):
        try:
            res_data = json.loads(request.body.decode("utf-8"))
        except:
            return Response(
                {"success": False, "message": "Service not available"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = decode_token(token)
        except:
            return Response(
                {"success": False, "message": "Token Expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if "email" not in payload:
            return Response(
                {"success": False, "message": "Invalid Token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = User.objects.filter(email=payload["email"]).first()
        if user is None:
            return Response(
                {"success": False, "message": "Email is not registered"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        password1 = res_data.get("password1", None)
        password2 = res_data.get("password2", None)
        if password1 and password2 is None:
            return Response(
                {"success": False, "message": "Provide valid Password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if password1 != password2:
            return Response(
                {"success": False, "message": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # employee = Employee.objects.filter(user=user).first()
        # if employee:
        #     employee.status = "active"
        #     employee.save()

        # company = Company.objects.filter(user=user).first()
        # if company:
        #     company.status = "active"
        #     company.is_active = True
        #     company.save()

        # vendor = Vendor.objects.filter(user=user).first()
        # if vendor:
        #     vendor.status = "active"
        #     vendor.is_active = True
        #     vendor.save()

        if user.last_login is user.vendor is user.employee is None:
            context = {
                "name": user.first_name,
                "email": user.email,
                "company": user.company.name,
            }

            send_success_mail("Register Succcess", "register-success.html", context)

        user.set_password(password1 and password2)
        user.is_active = True
        user.status = "active"
        user.save()
        context = {"name": user.first_name, "email": user.email}
        send_confirm_mail(
            "Password Change Notification",
            "password-changed-confirmation.html",
            context,
        )
        return Response(
            {"success": True, "message": "Password Successfully change"},
            status=status.HTTP_200_OK,
        )


import random

import requests
from decouple import config
from django.shortcuts import get_object_or_404


class LoginWithEmailOtpViewset(ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    serializer_class = LoginWithEmailOtpSerializer
    queryset = User.objects.all().order_by("-id")

    def create(self, request, *args, **kwargs):
        data = request.data
        otp_method = data["otp_method"]
        phone = data["phone"]

        if otp_method == "email":
            user_email = User.objects.filter(email=data["email"]).first()
            if not user_email:
                return Response(
                    {"success": False, "message": "Email is not registered with us!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                otp = generate_otp()
                context = {
                    "email": user_email.email,
                    "name": user_email.first_name,
                    "otp": otp,
                }
                user_email.otp = otp
                user_email.save()

                email_thread = threading.Thread(
                    target=send_otp_email,
                    args=("Your One Time Password", "account-otp.html", context),
                )
                email_thread.start()

                return Response(
                    {"success": True, "message": "Check your email for the OTP."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"success": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif otp_method == "phone":
            user = User.objects.filter(phone=phone).first()
            if not user:
                return Response(
                    {"success": False, "message": "Phone number not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if data["whatsapp_verified"] == True:
                api_url = "https://smswaapi.in/api/send?"
                number = request.data["phone"]
                otp = str(random.randint(1000, 9999))
                message = (
                    f"Dear Customer, your OTP is {otp}. Please enter it to verify your mobile number. Your OTP will "
                    f"expire in 10 minutes. Team Smartbuyer"
                )
                instance_id = config("INSTANCE_ID")
                access_token = config("ACCESS_TOKEN")

                user = get_object_or_404(User, phone=number)
                user.otp = otp
                user.whatsapp_verified = True
                user.save()

                params = {
                    "number": number,
                    "type": "text",
                    "message": message,
                    "instance_id": instance_id,
                    "access_token": access_token,
                }

                response = requests.get(api_url, params=params)
                if response.status_code == 200:
                    return Response(
                        {
                            "success": True,
                            "message": "Otp sent successfully",
                            "whatsapp_verified": user.whatsapp_verified,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                return Response(
                    {"success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                api_url = "http://kutility.org/app/smsapi/index.php?"
                contacts = request.data["phone"]
                sms_contacts = int(str(contacts)[2:])
                otp = str(random.randint(1000, 9999))
                message = f"SmartBuyer.co.in {otp} is the verification code to log in to your account. Please DO NOT SHARE this code with anyone VANKTC"

                user = get_object_or_404(User, phone=contacts)
                user.otp = otp
                user.whatsapp_verified = False
                user.save()

                params = {
                    "key": config("SMS_API_KEY"),
                    "campaign": config("CAMPAIGN"),
                    "routeid": 7,
                    "type": "text",
                    "contacts": sms_contacts,
                    "senderid": config("SENDERID"),
                    "msg": message,
                    "template_id": config("TEMPLATE_ID"),
                    "pe_id": config("PE_ID"),
                }

                response = requests.get(api_url, params=params)
                if response.status_code == 200:
                    return Response(
                        {
                            "success": True,
                            "message": "Otp sent successfully to your number",
                        },
                        status=status.HTTP_201_CREATED,
                    )
                return Response(
                    {"success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )


from django.contrib.auth.models import Group, Permission


class VerifyEmailOtpAndGiveTokenViewset(ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    serializer_class = VerifyLoginWithEmailOtpSerializer
    queryset = User.objects.all().order_by("-id")

    def create(self, request, *args, **kwargs):
        data = request.data
        email = data["email"]
        if email:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                otp = int(serializer.validated_data["otp"])

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return Response(
                        {
                            "success": False,
                            "message": "User with this email does not exist.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if user.otp == otp:
                    if user.last_login is not None:
                        user.otp = None
                        user.is_active = True
                        user.save()
                        refresh = RefreshToken.for_user(user)
                        access_token = str(refresh.access_token)
                        groups = Group.objects.filter(user=user)

                        group_data = [
                            {"id": group.id, "name": group.name} for group in groups
                        ]

                        user_permissions = Permission.objects.filter(user=user)
                        custom_group_permissions = Permission.objects.filter(
                            group__user=user
                        )

                        all_permissions_set = {
                            f"{perm.content_type.app_label}|{perm.codename}"
                            for perm in user_permissions
                        } | {
                            f"{perm.content_type.app_label}|{perm.codename}"
                            for perm in custom_group_permissions
                        }

                        all_permissions = sorted(list(all_permissions_set))

                        user_data = {
                            "user_id": user.id,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "phone": user.phone,
                            "role": group_data,
                            "permission": all_permissions,
                        }

                        data = {
                            "success": True,
                            "message": "Login Successful",
                            "data": {
                                "refresh": str(refresh),
                                "access": access_token,
                                "userData": user_data,
                            },
                        }

                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {
                                "success": False,
                                "message": "Password reset is required before first time login.",
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                else:
                    return Response(
                        {"success": False, "message": "Incorrect OTP."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"success": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            phone = data["phone"]
            if phone:
                serializer = self.serializer_class(data=data)
                if serializer.is_valid():
                    phone = serializer.validated_data["phone"]
                    otp = int(serializer.validated_data["otp"])

                    try:
                        user = User.objects.get(phone=phone)
                    except User.DoesNotExist:
                        return Response(
                            {
                                "success": False,
                                "message": "User with this phone does not exist.",
                            },
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    if user.otp == otp:
                        if user.last_login is not None:
                            user.otp = None
                            user.is_active = True
                            user.save()
                            refresh = RefreshToken.for_user(user)
                            access_token = str(refresh.access_token)

                            groups = Group.objects.filter(user=user)
                            group_data = [
                                {"id": group.id, "name": group.name} for group in groups
                            ]

                            user_permissions = Permission.objects.filter(user=user)
                            custom_group_permissions = Permission.objects.filter(
                                group__user=user
                            )

                            all_permissions_set = {
                                f"{perm.content_type.app_label}|{perm.codename}"
                                for perm in user_permissions
                            } | {
                                f"{perm.content_type.app_label}|{perm.codename}"
                                for perm in custom_group_permissions
                            }

                            all_permissions = sorted(list(all_permissions_set))

                            user_data = {
                                "user_id": user.id,
                                "email": user.email,
                                "first_name": user.first_name,
                                "last_name": user.last_name,
                                "phone": user.phone,
                                "role": group_data,
                                "permission": all_permissions,
                            }

                            data = {
                                "success": True,
                                "message": "Login Successful",
                                "data": {
                                    "refresh": str(refresh),
                                    "access": access_token,
                                    "userData": user_data,
                                },
                            }

                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            return Response(
                                {
                                    "success": False,
                                    "message": "Password reset is required before first time login.",
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    else:
                        return Response(
                            {"success": False, "message": "Incorrect OTP."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"success": False, "message": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )


import logging
from rest_framework.authentication import get_authorization_header
from django.db import IntegrityError
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import OutstandingToken


logger = logging.getLogger(__name__)


class LogoutViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Retrieve the access token from the Authorization header
            authorization_header = get_authorization_header(request).decode("utf-8")
            access_token = authorization_header.split(" ")[1]

            # Manually blacklist the access token
            try:
                OutstandingToken.objects.create(token=access_token)
            except IntegrityError:
                pass  # Token already exists, ignore

            # Log the user out (optional)
            logout(request)

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Logout failed"}, status=status.HTTP_400_BAD_REQUEST
            )
