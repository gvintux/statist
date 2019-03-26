from django.db import models
from django.utils import timezone


class Server(models.Model):
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
