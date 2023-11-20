from django.contrib import admin
from user.models import CustomGroup, User

# Register your models here.

admin.site.register(User)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sequence')  # Include 'sequence' field

admin.site.register(CustomGroup, CustomGroupAdmin)