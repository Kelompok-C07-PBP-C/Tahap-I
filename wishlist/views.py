from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from user_profile.models import BuyerProfile
from seller.models import ProductEntry
from .models import WishlistItem
import json

def show_wishlist(request):
    user_profile = BuyerProfile.objects.get(user=request.user)
    wishlist = WishlistItem.objects.filter(user=user_profile).first()
    products = wishlist.products.all() if wishlist else []
    return render(request, 'wishlist.html', {'products': products})


@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(ProductEntry, id=product_id)
        user_profile = BuyerProfile.objects.get(user=request.user)

        wishlist, created = WishlistItem.objects.get_or_create(user=user_profile, name='My Wishlist')
        wishlist.products.add(product)
        return JsonResponse({'success': True})


@csrf_exempt
def add_to_wishlist_from_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(ProductEntry, id=product_id)
        user_profile = BuyerProfile.objects.get(user=request.user)

        wishlist, created = WishlistItem.objects.get_or_create(user=user_profile, name='My Wishlist')
        wishlist.products.add(product)
        return redirect('wishlist:show_wishlist')


@csrf_exempt
def delete_wishlist_item(request, id):
    user_profile = BuyerProfile.objects.get(user=request.user)
    wishlist = WishlistItem.objects.filter(user=user_profile).first()
    if wishlist:
        product = get_object_or_404(ProductEntry, id=id)
        wishlist.products.remove(product)
    return redirect('wishlist:show_wishlist')


@csrf_exempt
def delete_wishlist_item_from_catalog(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(ProductEntry, id=product_id)
        user_profile = BuyerProfile.objects.get(user=request.user)

        wishlist = WishlistItem.objects.filter(user=user_profile).first()
        if wishlist:
            wishlist.products.remove(product)
        return JsonResponse({'success': True})


def get_wishlist_json(request):
    user_profile = BuyerProfile.objects.get(user=request.user)
    wishlist = WishlistItem.objects.filter(user=user_profile).first()
    products = wishlist.products.values('id', 'product_name', 'product_image', 'product_category') if wishlist else []
    return JsonResponse(list(products), safe=False)