from django.contrib import admin
from djnotty import models


class MessageToUserInline(admin.TabularInline):
    model = models.MessageToUser


class MessageToGroupInline(admin.TabularInline):
    model = models.MessageToGroup


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    inlines = [MessageToUserInline,MessageToGroupInline]
