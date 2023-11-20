from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from smartbuyerdemo import settings

# from company.models import Company

# from employee.models import Employee
# from vendor.models import Vendor


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    STATUS_CHOICES = (
        ("pending", "pending"),
        ("active", "active"),
        ("inactive", "inactive"),
    )
    username = models.CharField(max_length=60, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, default="")
    about_me = models.CharField(max_length=100, null=True)
    last_login = models.DateTimeField(_("last login"), null=True)
    email = models.EmailField(_("email address"), unique=True)
    profile_image = models.CharField(max_length=250, null=True)
    otp = models.IntegerField(null=True)
    whatsapp_otp = models.IntegerField(null=True)
    whatsapp_verified = models.BooleanField(default=False)
    designation = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=15, null=True)
    message = models.CharField(max_length=200, default="")
    is_active = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, default="Pending", max_length=25)
    role = models.CharField(max_length=15, null=True)
    aadhar_card = models.CharField(max_length=12, null=True)
    pancard = models.CharField(max_length=10, null=True)
    emergency_contact = models.CharField(max_length=15, null=True)
    current_address = models.CharField(max_length=150, null=True)
    permanent_address = models.CharField(max_length=150, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    # company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, null=True)
    # vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING, null=True)
    # employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"
        ordering = ["-id"]

    # def upload_presentation(self, file_to_upload):
    #     allowed_type = [".jpg", ".png"]
    #     file_name = "profile_image"
    #     self.profile_image, presigned_url = upload_file_to_bucket(
    #         file_to_upload, allowed_type, "ProfileImage/", self.id, None
    #     )


# class AuthGroupModel(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=150)

#     class Meta:
#         db_table = "auth_group"
#         managed = False


# class ContentTypeModel(models.Model):
#     id = models.AutoField(primary_key=True)
#     app_label = models.CharField(max_length=100)
#     model = models.CharField(max_length=100)

#     class Meta:
#         db_table = "django_content_type"
#         managed = False


# class AuthPermissionModel(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=255)
#     content_type = models.ForeignKey(ContentTypeModel, on_delete=models.DO_NOTHING)

#     class Meta:
#         db_table = "auth_permission"
#         managed = False


# class AuthGroupPermissionsModel(models.Model):
#     id = models.AutoField(primary_key=True)
#     group = models.ForeignKey(AuthGroupModel, on_delete=models.DO_NOTHING)
#     permission = models.ForeignKey(AuthPermissionModel, on_delete=models.DO_NOTHING)

#     class Meta:
#         db_table = "auth_group_permissions"
#         managed = False


# class UserGroupsModel(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
#     group = models.ForeignKey(AuthGroupModel, on_delete=models.DO_NOTHING)

#     class Meta:
#         db_table = "user_groups"
#         managed = False


# class CustomGroup(Group):
#     sequence = models.PositiveIntegerField()
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="group_created",
#     )
#     updated_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="group_updated",
#     )
#     created_at = models.DateTimeField(default=now)
#     updated_at = models.DateTimeField(default=now)

#     def save(self, *args, **kwargs):
#         if self.sequence is None:
#             last_record = (
#                 CustomGroup.objects.filter(created_by=self.created_by)
#                 .order_by("-sequence")
#                 .first()
#             )
#             self.sequence = (last_record.sequence + 1) if last_record else 1
#         super(CustomGroup, self).save(*args, **kwargs)
