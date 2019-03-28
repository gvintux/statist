import os
from django.core.management.base import BaseCommand
from servermon.models import Server, Event, Mailing
from django.core.mail import send_mail
from statist.settings import EMAIL_HOST_USER
from datetime import datetime


def ping(ip, num):
    return not os.system('ping -c %s %s >/dev/null 2>&1' % (num, ip))


class Command(BaseCommand):
    help = 'Updates servers link state'

    def add_arguments(self, parser):
        parser.add_argument('-c', default=1, help='specifies count of ping attempts')

    def handle(self, *args, **options):
        count = options['c']
        servers = Server.objects.all()
        failed_server_list = []
        arised_server_list = []
        for s in servers:
            ping_result = ping(s.ip, count)
            self.stdout.write(self.style.SUCCESS(str(ping_result)))
            log = Event.objects.filter(server=s).last()
            if ping_result:
                if log.is_online != ping_result:
                    l = Event(server=s, date=datetime.now(), is_online=ping_result)
                    l.save()
                    arised_server_list.append(s)
            if not ping_result:
                if log.is_online != ping_result:
                    l = Event(server=s, date=datetime.now(), is_online=ping_result)
                    l.save()
                failed_server_list.append(s)
        title = 'Состояние серверов на ' + str(datetime.now())
        report = ''
        if len(failed_server_list) > 0:
            report = report + 'Сервера офлайн\n'
            for s in failed_server_list:
                log = Event.objects.filter(server=s).last()
                report = report + log.__str__()
            report += '\n'
        if len(arised_server_list) > 0:
            report = report + 'Сервера онлайн\n'
            for s in arised_server_list:
                log = Event.objects.filter(server=s).last()
                report = report + log.__str__()
        if len(failed_server_list) > 0 or len(arised_server_list):
            mailing_list = Mailing.objects.all()
            emails = []
            for item in mailing_list:
                emails.append(item.address)
            send_mail(title, report, EMAIL_HOST_USER, emails, fail_silently=False)
