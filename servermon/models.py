from datetime import datetime
from django.db import models
from django.utils import timezone
import sys


class Server(models.Model):
    ip = models.CharField(max_length=15, verbose_name='IP')
    name = models.CharField(max_length=255, verbose_name='название')

    def __str__(self):
        return self.name + ' [%s]' % self.ip

    class Meta:
        verbose_name = 'сервер'
        verbose_name_plural = 'серверы'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        log = Event.objects.filter(server=self)
        if not log:
            l = Event(server=self, date=timezone.now(), is_online=True)
            l.save()


class Event(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, verbose_name='сервер')
    server.help_text = 'Выберите сервер из списка'
    date = models.DateTimeField(verbose_name='дата')
    date.help_text = 'Укажите время события'
    is_online = models.BooleanField(default=True, verbose_name='онлайн')
    is_online.help_text = 'Есть связь с сервером?'

    def delta_time(self):
        if self.is_online:
            last_offline_event = Event.objects.all().filter(server=self.server).filter(is_online=False).filter(
                date__lt=self.date).last()
            if not last_offline_event:
                return None
            delta = self.date - last_offline_event.date
            return str(delta).split('.', maxsplit=1)[0]
        else:
            last_online_event = Event.objects.all().filter(server=self.server).filter(is_online=True).filter(
                date__lt=self.date).last()
            if not last_online_event:
                return None
            delta = self.date - last_online_event.date
            #delta_from_now = datetime.now() - self.date
            return str(delta).split('.', maxsplit=1)[0]
        return None

    def failure_time(self):
        if self.is_online:
            return None
        last_online_event = Event.objects.all().filter(server=self.server).filter(is_online=True).filter(
            date__gt=self.date).first()
        delta = None
        if not last_online_event:
            delta = datetime.now() - self.date
        else:
            delta = last_online_event.date - self.date
        return str(delta).split('.', maxsplit=1)[0]

    def __str__(self):
        return '  %s ' % self.date + self.server.__str__()

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'события'


class Mailing(models.Model):
    address = models.EmailField(verbose_name='адрес')
    address.help_text = 'Укажите адрес электронной почты'

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        # fields = ['address']
        # labels = {'address': 'адрес'}
