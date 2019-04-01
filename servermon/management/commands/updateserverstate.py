import os
from django.core.management.base import BaseCommand
from servermon.models import Server, Event, Mailing
from django.core.mail import send_mail
from statist.settings import EMAIL_HOST_USER
from datetime import datetime


def ping(ip: str, num: str) -> bool:
    """Executes ping command

    If ping invocation was successful then system method would return 0 therefore we return negation of that value

    Command invocation is unix-specific

    Parameters:
        ip (str): The ip address of target server
        num (str): The count of ping packets to send

    Returns:
        bool: whether the server is accessible with specified ip
    """
    return not os.system('ping -c %s %s >/dev/null 2>&1' % (num, ip))


class Command(BaseCommand):
    """Describes custom updateserverstate command
        Run python3 manage.py updateserverstate to update servers' state
    """

    help = 'Updates servers link state'

    def add_arguments(self, parser):
        parser.add_argument('-c', default=1, help='specifies count of ping attempts')

    def handle(self, *args, **options):
        """Handles custom command action

            Parameters:
                args (list): a list of args
                options (dict): a dict of options
        """
        count = options['c']
        servers = Server.objects.all()
        failed_server_list = []
        arised_server_list = []
        # try to ping all registered servers
        for s in servers:
            ping_result = ping(s.ip, count)
            # lookup for last event about server in event log
            log = Event.objects.filter(server=s).last()
            # if server changed state offline -> online
            if ping_result and (log.is_online != ping_result):
                # register arising event for server
                Event(server=s, date=datetime.now(), is_online=ping_result).save()
                # append server to arised list
                arised_server_list.append(s)
            # if server is offline and it was online
            if not ping_result and (log.is_online != ping_result):
                Event(server=s, date=datetime.now(), is_online=ping_result).save()
                # append server to failed list
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
