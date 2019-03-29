from django.contrib import admin
from .models import Server, Event, Mailing


class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip']


class EventAdmin(admin.ModelAdmin):
    list_display = ['date', 'server', 'is_online', 'delta_time', 'failure_time']
    list_filter = ('date', 'server')
    readonly_fields = ['delta_time', 'failure_time']

    def delta_time(self, obj):
        return obj.delta_time()

    # delta_time.admin_order_field = 'date'
    delta_time.short_description = 'Дельта (мин)'
    #delta_time.empty_value_display = 'Впервые'

    def failure_time(self, obj):
        return obj.failure_time()

    failure_time.short_description = 'Простой (мин)'

class MailingAdmin(admin.ModelAdmin):
    list_display = ['address']


admin.site.register(Server, ServerAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Mailing, MailingAdmin)
admin.site.site_header = "Мониторинг серверов"
# admin.site.empty_value_display = ''
