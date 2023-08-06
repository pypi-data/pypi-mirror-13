# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.management.base import BaseCommand
from updater.check import run_check
import sys
import traceback


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            status, version = run_check(notify=False)
            sys.stdout.write("Django {version} is {status}".format(status=status, version=version))
            sys.exit(0)
        except Exception as e:
            sys.stderr.write(traceback.format_exc())
            sys.exit(1)
