from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from cart.cart import CartManager
from .models import Order, OrderItem
from .forms import CheckoutForm



def checkout_view(request):
    cart_manager = CartManager(request)
    cart = cart_manager.get_cart()

    # 🚫 Block checkout if cart is empty
    if not cart or not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    # 🚫 HARD BLOCK: OUT-OF-STOCK ITEMS
    for item in cart.items.select_related('product'):
        if item.product.stock <= 0:
            messages.error(
                request,
                f"{item.product.name} is out of stock. "
                "Please remove it from your cart."
            )
            return redirect('cart:cart_detail')

        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"Not enough stock for {item.product.name}. "
                f"Available: {item.product.stock}"
            )
            return redirect('cart:cart_detail')

    # ⛔ If blocked above, checkout NEVER starts

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            total_price = cart_manager.get_total_price()

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address'],
                total_price=total_price,
                status='pending',
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity,
                    custom_data=item.custom_data
                )

            # 🧹 Clear cart (stock is NOT touched here)
            cart.items.all().delete()

            return redirect('orders:order_success', order.id)

    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart
    })



def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def orders_list_view(request):
    # Get all orders for the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders_list.html', {'orders': orders})


@login_required
def cancel_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Allow cancellation only if order is not shipped/completed/cancelled
    if order.status in ['pending', 'paid', 'processing']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
    else:
        messages.warning(request, f"Order #{order.id} cannot be cancelled at this stage.")

    return HttpResponseRedirect(reverse('orders:orders_list'))


