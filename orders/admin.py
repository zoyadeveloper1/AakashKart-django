from django.contrib import admin
from .models import Order, OrderProduct, Payment


# ==================== ORDER PRODUCT INLINE ====================
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'ordered')
    can_delete = False


# ==================== ORDER ADMIN ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'phone',
        'email',
        'city',
        'total',
        'tax',
        'status',
        'created_at',
    )

    list_filter = ('status', 'created_at')

    search_fields = (
        'order_number',
        'first_name',
        'last_name',
        'email',
        'phone',
        'city',
    )

    list_per_page = 20
    inlines = [OrderProductInline]

    readonly_fields = ('order_number', 'created_at', 'updated_at')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'Full Name'


# ==================== PAYMENT ADMIN ====================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_id',
        'user',
        'payment_method',
        'amount_paid',
        'status',
        'created_at',
    )

    list_filter = ('status', 'payment_method')
    search_fields = ('payment_id', 'user__username')


# ==================== ORDER PRODUCT ADMIN ====================
@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'user',
        'product',
        'quantity',
        'price',
        'ordered',
    )

    list_filter = ('ordered',)
    search_fields = ('order__order_number', 'product__product_name')