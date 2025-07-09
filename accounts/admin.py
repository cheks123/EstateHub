from django.contrib import admin
from .models import Profile

# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'user_type')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('user_type',)

admin.site.register(Profile, ProfileAdmin)

