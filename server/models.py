from django.db import models
from django.utils import timezone


class Server(models.Model):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        log = Log.objects.filter(server=self)
        if not log:
            l = Log(server=self, date=timezone.now(), is_online=True)
            l.save()

    ip = models.CharField(max_length=15)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name + ' (%s)' % self.ip


class Log(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    date = models.DateTimeField()
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return '  %s ' % self.date + self.server.__str__() + ' ' + ('up' if self.is_online else 'down')
