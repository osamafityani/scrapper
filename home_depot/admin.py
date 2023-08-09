from django.contrib import admin
from import_export.admin import ExportActionMixin
from home_depot.models import Product


class ProductExportAllFields(ExportActionMixin, admin.ModelAdmin):
    list_display = ('link', 'current_price', 'last_price')


admin.site.register(Product, ProductExportAllFields)
