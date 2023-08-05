from django.contrib import admin

from .models import Heartbeat


class HeartbeatAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "updated_at"
    ]
    ordering = ["id", ]

admin.site.register(Heartbeat, HeartbeatAdmin)
