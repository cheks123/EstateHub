from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('upload/', views.upload_property, name='upload_property'),
    path('<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('property/<int:pk>/edit/', views.edit_property, name='edit_property'),
    path('property/<int:pk>/delete/', views.delete_property, name='delete_property'),
    # From Grok
    path('image/<int:image_id>/delete/', views.delete_property_image, name='delete_property_image'),
    path('image/<int:image_id>/update/', views.update_property_image, name='update_property_image'),
    path('<int:pk>/add-image/', views.add_property_image, name='add_property_image'),
]
