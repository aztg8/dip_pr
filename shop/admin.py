from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *

admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_display', 'price', 'category']

    def image_display(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;" />')

    image_display.short_description = 'Фото'


admin.site.register(Profile)

admin.site.register(Review)


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name',
                    'phone_number', 'address',  'city', 'paid',
                    'order_items_display', 'created', 'updated', 'email']
    inlines = [OrderItemInline]

    def order_items_display(self, obj):
        items = obj.items.all()
        item_str = ', '.join([f'{item.product.title} (x{item.quantity})' for item in items])
        return item_str

    order_items_display.short_description = 'Товары'


admin.site.register(Order, OrderAdmin)
