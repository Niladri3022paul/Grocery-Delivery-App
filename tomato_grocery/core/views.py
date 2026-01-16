from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product, CartItem, Order

def home(request):
    return render(request, 'home.html')

def menu(request):
    categories = Category.objects.all()
    products = Product.objects.all()  
    return render(request, 'menu.html', {'categories': categories, 'products': products})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product, defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} added to cart!')
    return redirect('menu')

@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'cart.html', {'items': items, 'total': total})

@login_required
def checkout(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        if not address:
            messages.error(request, 'Please provide a delivery address.')
            return render(request, 'checkout.html')
        items = CartItem.objects.filter(user=request.user)
        if not items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')
        order = Order.objects.create(user=request.user, address=address)
        order.items.set(items)
        items.delete()  
        messages.success(request, 'Order placed successfully!')
        return redirect('home')
    return render(request, 'checkout.html')