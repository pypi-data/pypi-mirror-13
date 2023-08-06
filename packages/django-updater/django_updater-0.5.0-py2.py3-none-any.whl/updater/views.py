# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from .models import Status
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from .package import run_check
from .util import is_allowed_host, is_allowed_ip


def run_view(request, token):
    """
    This is the view that kicks off the process to check for updates.
    :param request:
    :param token:
    :return:
    """
    if not is_allowed_host(request) or not is_allowed_ip(request):
        raise PermissionDenied

    if not Status.objects.filter(site_token=token).exists():
        raise PermissionDenied

    if not request.GET.get("health", False):
        run_check(registered=request.GET.get("registered", False))
    return HttpResponse("ok")

