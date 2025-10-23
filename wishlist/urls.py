from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.show_wishlist, name='show_wishlist'), # Menampilkan halaman wishlist
    path('wishlist/delete/<int:id>/', views.delete_wishlist_item, name='delete_wishlist_item'), # Hapush wishlist berdasarkan id
    path('add/', views.add_to_wishlist, name='add_to_wishlist'), # Menambahkan ke wishlist
    path('add_from_details/', views.add_to_wishlist_from_details, name='add_from_details'), # 
    path('delete/', views.delete_wishlist_item_from_catalog, name='delete_wishlist_item_from_catalog'),
    path('json/', views.get_wishlist_json, name="get_wishlist_json")
]