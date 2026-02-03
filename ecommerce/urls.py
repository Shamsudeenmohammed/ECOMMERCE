from django.contrib import admin
from django.urls import path, include
from .views import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('getout/', admin.site.urls),
    path('', home_view, name='home'),

    path('products/', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
]

# ✅ THIS SERVES MEDIA FILES IN DEVELOPMENT
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )