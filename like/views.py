import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from user_profile.models import BuyerProfile
from seller.models import ProductEntry
from like.models import Like
from wishlist.models import WishlistItem

@csrf_exempt
@login_required
def add_like(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id') or json.loads(request.body).get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'error': 'No product ID provided'})

        buyer_profile = get_object_or_404(BuyerProfile, user=request.user)
        product = get_object_or_404(ProductEntry, pk=product_id)

        # Simpan ke Like
        like, created = Like.objects.get_or_create(user=buyer_profile, product=product)

        # Tambahkan juga ke Wishlist
        wishlist_item, _ = WishlistItem.objects.get_or_create(name=product.product_name)
        wishlist_item.user.add(buyer_profile)
        wishlist_item.products.add(product)

        return JsonResponse({'success': True, 'liked': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
@login_required
def delete_like_from_catalog(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id') or json.loads(request.body).get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'error': 'No product ID provided'})

        buyer_profile = get_object_or_404(BuyerProfile, user=request.user)
        product = get_object_or_404(ProductEntry, pk=product_id)

        # Hapus dari Like
        Like.objects.filter(user=buyer_profile, product=product).delete()

        # Hapus juga dari Wishlist
        wishlist_item = WishlistItem.objects.filter(name=product.product_name, user=buyer_profile).first()
        if wishlist_item:
            wishlist_item.products.remove(product)
            if wishlist_item.products.count() == 0:
                wishlist_item.delete()

        return JsonResponse({'success': True, 'liked': False})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})