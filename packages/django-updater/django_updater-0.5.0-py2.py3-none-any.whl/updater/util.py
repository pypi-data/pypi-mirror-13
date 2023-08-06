# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
import socket

from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django import conf

from .conf import settings

logger = logging.getLogger(__name__)


def send_notification(result):
    """
    Sends a notification.
    :param result: Dictionary containing all updates and security issues
    :return: True if all notifcations have been sent successfully
    """
    # only mails are supported right now. This might change, so we go for the more generic `send_notification`
    # as method name, but use it as a proxy to send_mail
    return send_mail(result, mail_from=conf.settings.SERVER_EMAIL, mail_to=settings.UPDATER_EMAILS)


def send_mail(result, mail_from, mail_to, fail_sitently=False):
    """
    Sends a notification email.
    :param result: Dictionary containing all updates and security issues
    :return: :bool: True if mail has been send successfully
    """

    subject = "Important: Security updates on %s" % result["site"] if result["security"] \
        else "Updates available on %s" % result["site"]
    txt_message = render_to_string("summary.txt", result)
    html_message = render_to_string("summary.html", result)
    mail = EmailMultiAlternatives(
        subject, txt_message, mail_from, mail_to)
    mail.attach_alternative(html_message, 'text/html')
    return mail.send(fail_silently=fail_sitently)


def is_allowed_host(request, allowed_hosts=settings.UPDATER_ALLOWED_HOSTS):
    """
    Gets all associated IP addresses of `allowed_hosts` and checks if the requesting ip is one of them
    :param request: request object
    :param allowed_hosts: list of allowed hosts, `"*"` matches everything
    :return:
    """
    if "*" in allowed_hosts:
        return True
    ip = get_client_ip(request)

    for host in allowed_hosts:
        if ":" in host:
            host, port = host.split(":")
        else:
            port = None

        try:
            # getaddrinfo returns a list of 5 tuples in which we are only interested in the first tuple of the
            # fourth tuple
            if ip in [resp[4][0] for resp in socket.getaddrinfo(host, port)]:
                return True
        except socket.gaierror as e:
            logger.warning("Unable to get IP address for hostname {}".format(host))

    return False


def is_allowed_ip(request, allowed_ips=settings.UPDATER_ALLOWED_IPS):
    return "*" in allowed_ips or get_client_ip(request) in allowed_ips


def get_client_ip(request):
    """
    http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    :param request:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip