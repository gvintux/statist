import os
from django.core.management.base import BaseCommand
from server.models import Server, Log
from django.utils import timezone


def ping(ip, num):
    return not os.system('ping -c %s %s >/dev/null 2>&1' % (num, ip))


class Command(BaseCommand):
    help = 'Updates server uplink state'

    def add_arguments(self, parser):
        parser.add_argument('-c', default=1, help='specifies count of ping attempts')

    def handle(self, *args, **options):
        count = options['c']
        servers = Server.objects.all()
        for s in servers:
            ping_result = ping(s.ip, count)
            self.stdout.write(self.style.SUCCESS(str(ping_result)))
            log = Log.objects.filter(server=s).last()
            if log.is_online != ping_result:
                l = Log(server=s, date=timezone.now(), is_online=ping_result)
                l.save()
