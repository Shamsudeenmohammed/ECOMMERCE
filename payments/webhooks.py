import hmac
import hashlib
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from orders.models import Order
from products.models import Product
from .models import Payment


@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    signature = request.headers.get('x-paystack-signature')

    computed_signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=payload,
        digestmod=hashlib.sha512
    ).hexdigest()

    if signature != computed_signature:
        return HttpResponse(status=400)

    event = json.loads(payload)

    if event.get('event') == 'charge.success':
        reference = event['data']['reference']
        metadata = event['data']['metadata']
        order_id = metadata.get('order_id')

        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(reference=reference)

                # 🔒 Prevent double processing
                if payment.status == 'succeeded':
                    return HttpResponse(status=200)

                order = Order.objects.select_for_update().get(id=order_id)

                # 🔻 Reduce stock
                for item in order.items.select_related('product'):
                    product = item.product

                    if product.stock < item.quantity:
                        # Safety fallback (should never happen)
                        return HttpResponse(status=400)

                    product.stock -= item.quantity

                    # 🚨 Mark out of stock
                    if product.stock == 0:
                        product.is_active = False

                    product.save(update_fields=['stock', 'is_active'])

                # ✅ Mark payment & order as successful
                payment.status = 'succeeded'
                payment.save(update_fields=['status'])

                order.status = 'paid'
                order.save(update_fields=['status'])

        except (Payment.DoesNotExist, Order.DoesNotExist):
            pass

    return HttpResponse(status=200)
