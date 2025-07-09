from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Property, PropertyImage, Comment

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'property_type', 'created_at')
    search_fields = ('title', 'location', 'description')
    inlines = [PropertyImageInline]

admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImage)
admin.site.register(Comment)

