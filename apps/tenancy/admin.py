from django.contrib import admin

from . import models


@admin.register(models.Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'code')


@admin.register(models.TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary', 'tenant')
    search_fields = ('domain', 'tenant__name', 'tenant__code')


@admin.register(models.TenantSetting)
class TenantSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('key', 'tenant__name', 'tenant__code')