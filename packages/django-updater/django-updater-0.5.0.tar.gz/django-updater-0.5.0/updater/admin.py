# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import json
from django.contrib import admin
from django.conf.urls import url
from django.http import HttpResponse
from .models import Status
from updater.check import run_check
import time


class StatusAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        # don't display the app on the index site
        return False

    def get_urls(self):
        urls = super(StatusAdmin, self).get_urls()
        return [
            url(r'^update-status/$', self.admin_site.admin_view(self.registration_status_view),
                name="update-status"),
        ] + urls

    def registration_status_view(self, request):
        request.current_app = self.admin_site.name
        status, version = run_check(notify=False)
        data = {
            "status": status,
            "version": version,
            "run_again_at": time.time() + 60 * 60 * 24
        }
        request.session["updater_admin_run"] = data
        return HttpResponse(json.dumps(data), content_type="application/json")

admin.site.register(Status, StatusAdmin)