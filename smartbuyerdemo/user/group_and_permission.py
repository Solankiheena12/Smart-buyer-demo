# from django.contrib.auth.models import Group, Permission
# from django.contrib.contenttypes.models import ContentType


# from rest_framework.viewsets import ModelViewSet
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework_simplejwt.authentication import JWTAuthentication

# from user.models import AuthGroupPermissionsModel, CustomGroup, User
# from user.models import AuthPermissionModel

# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.viewsets import ModelViewSet

# from user.models import User, AuthPermissionModel
# from .serializers import CustomGroupSerializers, PermissionSerializers
# from rest_framework.filters import SearchFilter, OrderingFilter


# class GroupViewSet(ModelViewSet):
#     queryset = Group.objects.all()
#     serializer_class = CustomGroupSerializers

#     filter_backends = [SearchFilter, OrderingFilter]
#     search_fields = ["name"]
#     ordering_fields = ["name"]

#     def create(self, request, *args, **kwargs):
#         data = request.data
#         serializer = CustomGroupSerializers(data=data)

#         if serializer.is_valid():
#             serializer.validated_data["created_by"] = request.user
#             serializer.save()

#             return Response(
#                 {"success": True, "data": serializer.data},
#                 status=status.HTTP_201_CREATED,
#             )
#         else:
#             return Response(
#                 {"success": False, "message": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     def list(self, request, *args, **kwargs):
#         user = request.user
#         queryset = CustomGroup.objects.filter(created_by=user.id)
#         queryset = queryset.exclude(id__in=[1, 2, 3])
#         serializer = CustomGroupSerializers(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def update(self, request, *args, **kwargs):
#         data = request.data
#         instance = self.get_object()

#         serializer = self.serializer_class(instance, data=data, partial=True)

#         if serializer.is_valid():
#             instance.save()
#             return Response(
#                 {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
#             )
#         else:
#             return Response(
#                 {"success": False, "message": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


# class AssignUserGroupViewSet(ModelViewSet):
#     queryset = Group.objects.all()
#     serializer_class = CustomGroupSerializers

#     def create(self, request, *args, **kwargs):
#         user_ids = request.data.get("user_id")
#         user_list = User.objects.filter(pk__in=user_ids)
#         group_id = request.data.get("group_id")
#         try:
#             group = Group.objects.get(pk=group_id)
#         except Group.DoesNotExist:
#             return Response(
#                 {"success": False, "message": "Group does not exist"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if len(user_list) != len(user_ids):
#             return Response(
#                 {"success": False, "message": "Users do not exist"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         for user in user_list:
#             group.user_set.add(user)

#         return Response(
#             {"success": True, "message": "User assigned to group"},
#             status=status.HTTP_200_OK,
#         )


# from rest_framework.permissions import IsAuthenticated
# from decouple import config


# class GroupPermissionViewSet(ModelViewSet):
#     queryset = Permission.objects.filter(content_type_id__gt=5)
#     serializer_class = PermissionSerializers
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def list(self, request, *args, **kwargs):
#         user = request.user
#         user_groups = user.groups.all()

#         if user_groups:
#             group = user_groups.first()
#             group_permissions = group.permissions.filter(content_type_id__gt=5)
#             queryset = self.get_queryset()

#             page = self.paginate_queryset(queryset)
#             if page is not None:
#                 serializer = self.get_serializer(page, many=True)
#                 return self.get_paginated_response(serializer.data)

#             serializer = self.get_serializer(group_permissions, many=True)
#         return Response(serializer.data)

#     # def list(self, request, *args, **kwargs):
#     #     permissions = self.get_queryset()
#     #     permission_list = []

#     #     for permission in permissions:
#     #         permission_str = f"{permission.content_type.app_label} | {permission.name}"
#     #         permission_dict = {
#     #             "id": permission.id,
#     #             "permission": permission_str
#     #         }
#     #         permission_list.append(permission_dict)

#     #     return Response(permission_list)


# class GetGroupPermissionViewSet(ModelViewSet):
#     queryset = Permission.objects.all()
#     serializer_class = PermissionSerializers
#     lookup_field = "id"

#     def retrieve(self, request, *args, **kwargs):
#         data = {}
#         group_id = self.kwargs.get("id")
#         print(group_id)
#         try:
#             group = Group.objects.get(pk=group_id)
#         except Group.DoesNotExist:
#             data["total_record"] = 0
#             data["success"] = False
#             data["message"] = "Group not found"
#             data["data"] = []
#             return Response(data=data, status=status.HTTP_404_NOT_FOUND)

#         permission_list = {}

#         for permission in group.permissions.all():
#             app_label = permission.content_type.app_label
#             codename = permission.codename

#             if app_label in permission_list:
#                 permission_list[app_label].append(codename)
#             else:
#                 permission_list[app_label] = [codename]

#         data["total_record"] = len(permission_list)
#         data["success"] = True
#         data["message"] = "OK"
#         data["data"] = permission_list
#         return Response(data=data, status=status.HTTP_200_OK)


# class AssignPermissionGroupViewSet(ModelViewSet):
#     queryset = Permission.objects.all()
#     serializer_class = PermissionSerializers

#     def create(self, request, *args, **kwargs):
#         group_id = request.data.get("group_id")
#         codename_list = list(request.data.get("codename"))

#         group = Group.objects.get(pk=group_id)
#         for codename in codename_list:
#             code_id = (
#                 Permission.objects.filter(codename=codename).values("id")[0].get("id")
#             )
#             group.permissions.add(code_id)

#         group_permission = Permission.objects.filter(group=group)
#         permission_list = {}
#         for permission in group_permission:
#             if permission.content_type.app_label in permission_list:
#                 permission_name = permission_list[permission.content_type.app_label]
#                 permission_list[permission.content_type.app_label] = ",".join(
#                     [permission_name, permission.name.split(" ")[1]]
#                 )
#             else:
#                 permission_list[
#                     permission.content_type.app_label
#                 ] = permission.name.split(" ")[1]

#         return Response(
#             {
#                 "success": True,
#                 "message": "Permission assigned to group",
#                 "response": permission_list,
#             },
#             status=status.HTTP_200_OK,
#         )


# class GetAllPermissionViewSet(ModelViewSet):
#     queryset = Permission.objects.all()
#     serializer_class = PermissionSerializers

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


# class CreateGroupWithPermissionsViewSet(ModelViewSet):
#     queryset = Group.objects.all()
#     serializer_class = CustomGroupSerializers
#     filter_backends = [OrderingFilter, SearchFilter]
#     ordering_fields = ["name", "sequence"]
#     search_fields = ["name"]

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         search_param = self.request.query_params.get("search", None)
#         ordering_param = self.request.query_params.get("ordering", None)

#         if search_param:
#             queryset = queryset.filter(name__icontains=search_param)

#         if ordering_param:
#             queryset = queryset.order_by(ordering_param)

#         return queryset

#     def list(self, request, *args, **kwargs):
#         groups = self.get_queryset()
#         group_list = []

#         for group in groups:
#             permissions = [
#                 {
#                     "id": permission.id,
#                     "permission": f"{permission.content_type.app_label}| {permission.name}",
#                 }
#                 for permission in group.permissions.all()
#             ]

#             custom_group = CustomGroup.objects.filter(name=group).first()

#             group_list.append(
#                 {
#                     "group_id": group.id,
#                     "group_name": group.name,
#                     "sequence": custom_group.sequence if custom_group else None,
#                     "permissions": permissions,
#                 }
#             )

#         return Response(
#             {"success": True, "response": group_list}, status=status.HTTP_200_OK
#         )

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()

#         permissions = [
#             {
#                 "id": permission.id,
#                 "permission": f"{permission.content_type.app_label} | {permission.name}",
#             }
#             for permission in instance.permissions.all()
#         ]

#         custom_group = CustomGroup.objects.filter(name=instance).first()

#         group_data = {
#             "group_id": instance.id,
#             "group_name": instance.name,
#             "sequence": custom_group.sequence if custom_group else None,
#             "permissions": permissions,
#         }

#         return Response(
#             {"success": True, "response": group_data}, status=status.HTTP_200_OK
#         )

#     def create(self, request, *args, **kwargs):
#         group_name = request.data.get("group_name")
#         permission_ids = request.data.get("permissions", [])
#         group = Group.objects.filter(name=group_name).exists()

#         if group:
#             return Response(
#                 {"success": False, "error": "Group name already exists"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Create the CustomGroup instance, which will automatically assign a sequence
#         custom_group = CustomGroup(name=group_name, created_by=request.user)
#         custom_group.save()

#         permissions = Permission.objects.filter(id__in=permission_ids)
#         custom_group.permissions.set(permissions)

#         permission_list = {}
#         for permission in custom_group.permissions.all():
#             if permission.content_type.app_label in permission_list:
#                 permission_name = permission_list[permission.content_type.app_label]
#                 permission_list[permission.content_type.app_label] = ",".join(
#                     [permission_name, permission.name.split(" ")[1]]
#                 )
#             else:
#                 permission_list[
#                     permission.content_type.app_label
#                 ] = permission.name.split(" ")[1]

#         return Response(
#             {
#                 "success": True,
#                 "message": "Group created and Permission assigned to Group",
#                 "response": permission_list,
#                 "sequence": custom_group.sequence,
#             },
#             status=status.HTTP_200_OK,
#         )

#     def update(self, request, *args, **kwargs):
#         group = self.get_object()
#         group_name = request.data.get("group_name")
#         permission_ids = request.data.get("permissions", [])

#         # You can add validation and error handling here if needed.
#         if group_name:
            
#             group.name = group_name
#             group.save()

#         if permission_ids:
#             permissions = Permission.objects.filter(id__in=permission_ids)
#             group.permissions.set(permissions)

#         permission_list = {}
#         for permission in group.permissions.all():
#             if permission.content_type.app_label in permission_list:
#                 permission_name = permission_list[permission.content_type.app_label]
#                 permission_list[permission.content_type.app_label] = ",".join(
#                     [permission_name, permission.name.split(" ")[1]]
#                 )
#             else:
#                 permission_list[
#                     permission.content_type.app_label
#                 ] = permission.name.split(" ")[1]

#         custom_group = CustomGroup.objects.get(name=group)

#         return Response(
#             {
#                 "success": True,
#                 "message": "Group updated and Permission assigned to Group",
#                 "group_id": group.id,
#                 "group": group.name,
#                 "permissions": permission_list,
#                 "sequence": custom_group.sequence,
#             },
#             status=status.HTTP_200_OK,
#         )

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.delete()
#         instance.save()
#         return Response(
#             {"success": True, "message": "Role Deleted"}, status=status.HTTP_200_OK
#         )


# class DeleteGroupWithPermissionsViewSet(ModelViewSet):
#     queryset = Group.objects.all()
#     serializer_class = CustomGroupSerializers

#     def create(self, request, *args, **kwargs):
#         group_ids = request.data.get("group_ids", [])

#         if not group_ids:
#             return Response(
#                 {"message": "No group IDs provided for deletion."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         deleted_groups = Group.objects.filter(id__in=group_ids).delete()

#         return Response(
#             {"success": True, "message": "Groups deleted successfully"},
#             status=status.HTTP_200_OK,
#         )
