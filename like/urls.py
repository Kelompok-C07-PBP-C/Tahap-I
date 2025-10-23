from django.urls import path
from . import views

app_name = 'like'

urlpatterns = [
    path('add/', views.add_like, name='add_like'),
    path('delete/', views.delete_like_from_catalog, name='delete_like_from_catalog'),
]