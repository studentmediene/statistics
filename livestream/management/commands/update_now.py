#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import floor
from sys import argv
from datetime import date, datetime
from glob import glob

from django.core.management.base import BaseCommand, CommandError

from livestream.tasks import update_recent_shows, create_plots

class Command(BaseCommand):
    help = "Update recent shows and create plots."

    def handle(self, *args, **kwargs):
        print "Updating shows..."
        update_recent_shows.delay()
        print "Creating plots..."
        create_plots.delay()
        print "Done!"
