# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import requests

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:  # pragma: no cover
    # django < 1.7 compatibility
    from django.contrib.sites.models import get_current_site
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django import conf, get_version

from .conf import settings


def run_check(notify=True):
    """
    Main entrypoint for all update checks. Fetches issues and updates and decides if a
    notification is sent.
    :param notify: (Optional) send notifications
    :return: tuple containing the status and the version currently in use
    """
    r = requests.get("/".join([settings.UPDATER_BASE_URL, "django.json"]))
    releases = r.json()["releases"]
    used_version = get_version()
    status = releases.get(used_version, "unknown")
    if notify and settings.UPDATER_NOTIFY and status in ["insecure", "outdated"]:
        send_notification(status, used_version)
    return status, used_version


def send_notification(status, version):
    """
    Sends a notification.
    :param status: the status of the used version "insecure" or "outdated"
    :param version: used django version
    :return: True if all notifcations have been sent successfully
    """
    # only mails are supported right now. This might change, so we go for the more generic
    # `send_notification` as method name, but use it as a proxy to send_mail
    return send_mail(status, version,
                     mail_from=conf.settings.SERVER_EMAIL, mail_to=settings.UPDATER_EMAILS)


def send_mail(status, version, mail_from, mail_to, fail_silently=False):
    """
    Sends a notification email.
    :param status: the status of the used version "insecure" or "outdated"
    :param version: used django version
    :param mail_from: mail address that is used as the sender
    :param mail_to: mail address to send the mail to
    :param fail_silently:
    :return: :bool: True if mail has been send successfully
    """
    site = get_current_site(None)
    subject = "Important: Security update for %s" % site if status == "insecure" \
        else "Update available for %s" % site
    context = {"status": status, "version": version, "site": site}
    txt_message = render_to_string("mail.txt", context=context)
    html_message = render_to_string("mail.html", context=context)
    mail = EmailMultiAlternatives(
        subject, txt_message, mail_from, mail_to)
    mail.attach_alternative(html_message, 'text/html')
    return mail.send(fail_silently=fail_silently)
