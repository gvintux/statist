from datetime import datetime
from django.db import models


class Server(models.Model):
    """Server model

    Attributes:
        ip: A CharField for ip address of the server
        name: A CharField for name of the server
    """
    ip = models.CharField(max_length=15, verbose_name='IP')
    ip.help_text = 'IP адрес вида XXX.XXX.XXX.XXX'
    name = models.CharField(max_length=255, verbose_name='название')
    name.help_text = 'Любое понятное описание'

    def __str__(self):
        """Returns server object string representation"""
        return self.name + ' [%s]' % self.ip

    class Meta:
        """Server model meta attributes"""
        verbose_name = 'сервер'
        verbose_name_plural = 'серверы'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Saves object in storage

            Also writes initial event object
        """
        super().save(force_insert, force_update, using, update_fields)
        existing_event = Event.objects.filter(server=self)
        if not existing_event:
            Event(server=self, date=datetime.now(), is_online=True).save()


class Event(models.Model):
    """Event model

    Attributes:
        server: Server ForeignKey related to the event
        date: DateTimeField when the event was occured
        is_online: BooleanField whether server is online
    """
    server = models.ForeignKey(Server, on_delete=models.CASCADE, verbose_name='сервер')
    server.help_text = 'Выберите сервер из списка'
    date = models.DateTimeField(verbose_name='дата')
    date.help_text = 'Укажите время события'
    is_online = models.BooleanField(default=True, verbose_name='онлайн')
    is_online.help_text = 'Есть связь с сервером?'

    def delta_time(self):
        """Calculates how long server was in previous state till current

        Returns:
            string: time delta without microseconds
        """
        delta = None
        if self.is_online:
            last_offline_event = Event.objects.all().filter(server=self.server).filter(is_online=False).filter(
                date__lt=self.date).last()
            if not last_offline_event:
                return None
            delta = self.date - last_offline_event.date
        else:
            last_online_event = Event.objects.all().filter(server=self.server).filter(is_online=True).filter(
                date__lt=self.date).last()
            if not last_online_event:
                return None
            delta = self.date - last_online_event.date
        return str(delta).split('.', maxsplit=1)[0]

    def failure_time(self):
        """Calculates how long offline server is in failure state

        Returns:
            string: time delta without microseconds
        """
        if self.is_online:
            return None
        next_online_event = Event.objects.all().filter(server=self.server).filter(is_online=True).filter(
            date__gt=self.date).first()
        delta = None
        if not next_online_event:
            delta = datetime.now() - self.date
        else:
            delta = next_online_event.date - self.date
        return str(delta).split('.', maxsplit=1)[0]

    def __str__(self):
        """Returns event object string representation"""
        return '  %s ' % self.date + self.server.__str__()

    class Meta:
        """Event model meta attributes"""
        verbose_name = 'событие'
        verbose_name_plural = 'события'


class Mailing(models.Model):
    """Mailing model

    Attributes:
        address: EmailField where to send notifications
    """
    address = models.EmailField(verbose_name='адрес')
    address.help_text = 'Укажите адрес электронной почты'

    def __str__(self):
        """Returns mailing object string representation"""
        return self.address

    class Meta:
        """Mailing model meta attributes"""
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
