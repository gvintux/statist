from django.contrib import admin
from .models import Server, Event, Mailing


class ServerAdmin(admin.ModelAdmin):
    """ServerAdmin meta attributes"""
    list_display = ['name', 'ip']


class EventAdmin(admin.ModelAdmin):
    """EventAdmin meta attributes"""
    list_display = ['date', 'server', 'is_online', 'delta_time', 'failure_time']
    list_filter = ('date', 'server')
    readonly_fields = ['delta_time', 'failure_time']

    def delta_time(self, obj):
        """Invokes event method"""
        return obj.delta_time()

    delta_time.short_description = 'Дельта (мин)'

    def failure_time(self, obj):
        """Invokes event method"""
        return obj.failure_time()

    failure_time.short_description = 'Простой (мин)'


class MailingAdmin(admin.ModelAdmin):
    """EventAdmin meta attributes"""
    list_display = ['address']


# register models in admin
admin.site.register(Server, ServerAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Mailing, MailingAdmin)
admin.site.site_header = "Мониторинг серверов"
