#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
from datetime import date, datetime
from glob import glob

from django.core.management.base import BaseCommand, CommandError

from livestream.parse import parse_access_log
from livestream.views import load_correct_access_log_files, load_and_merge_files, get_listeners_in_interval, get_total_listening_time

class Command(BaseCommand):
    format = "Format: python manage.py totaltime 2014-01-01T00:00:00 2014-01-01T01:00:01"
    error = "Wrong date format. " + format
    help = "Get total listening time in interval. " + format
    args = "<dt dt>"

    def handle(self, *args, **kwargs):
        if len(args) != 2:
            raise CommandError(self.error)

        try:
            starttime = datetime.strptime(args[0], "%Y-%m-%dT%H:%M:%S")
            endtime = datetime.strptime(args[1], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise CommandError(self.error)

        files = load_correct_access_log_files(starttime, endtime)
        merged_lines = load_and_merge_files(files)
        parsed_file = parse_access_log(merged_lines)

        (unique_listeners, listeners_in_interval) = get_listeners_in_interval(parsed_file, starttime, endtime)
        self.stdout.write("Total time spent listening between %s and %s: %d" % (str(starttime), str(endtime), get_total_listening_time(listeners_in_interval),))
