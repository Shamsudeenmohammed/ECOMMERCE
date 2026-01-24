from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False  # prevent deletion
    readonly_fields = ('product', 'price', 'quantity', 'custom_data')  # make all fields read-only

    # Prevent adding new items
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'phone_number',
        'total_price',
        'status',
        'created_at',
    )

    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    list_display_links = ('id', 'full_name')

    readonly_fields = (
        'full_name',
        'email',
        'phone_number',
        'address',
        'total_price',
        'created_at',
    )

    inlines = [OrderItemInline]
