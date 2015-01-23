# coding=utf-8
from django.contrib import admin
from .models import SocialGroup


class SocialGroupAdmin(admin.ModelAdmin):
    readonly_fields = ['name']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(SocialGroup, SocialGroupAdmin)