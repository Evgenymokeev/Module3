from django.contrib import admin
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import User, Product, Purchase, Return

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class ProductAdmin(AdminRequiredMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity_in_stock', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

class ReturnAdmin(AdminRequiredMixin, admin.ModelAdmin):
    list_display = ('purchase', 'created_at')
    actions = ['approve_return', 'reject_return']

    def approve_return(self, request, queryset):
        for return_request in queryset:
            product = return_request.purchase.product
            product.quantity_in_stock += return_request.purchase.quantity
            product.save()
            return_request.purchase.user.wallet += return_request.purchase.get_total_price()
            return_request.purchase.user.save()
            return_request.purchase.delete()
            return_request.delete()

    def reject_return(self, request, queryset):
        queryset.delete()

admin.site.register(User)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase)
admin.site.register(Return, ReturnAdmin)

