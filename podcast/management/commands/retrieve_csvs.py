#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
from datetime import date, datetime
from glob import glob

from django.core.management.base import BaseCommand, CommandError
from podcast.models import Show, PodcastStatistics
from statistics.settings import FEEDBURNER_EMAIL, FEEDBURNER_PASSWORD, DEBUG

import spynner, os, sys, io, csv
from PyQt4.QtCore import Qt
from bs4 import BeautifulSoup

BASE_URL = "http://feedburner.google.com"

class Command(BaseCommand):
    format = "Format: python manage.py retrieve-csvs"
    help = "Retrieve all CSVs from Feedburner. " + format

    def handle(self, *args, **kwargs):
        b = spynner.Browser()
        if DEBUG:
            b.show()
        print("Started...")

        b.load("http://feedburner.google.com")
        print("Loaded Feedburner...")

        b.wk_fill('input[name=Email]', FEEDBURNER_EMAIL)
        b.wk_click('#next')
        b.wait_load()
        b.wk_fill('input[name=Passwd]', FEEDBURNER_PASSWORD)

        b.wk_click('#signIn')
        print("Signing in...")

        b.wait_load()

        b.load("https://feedburner.google.com/fb/a/myfeeds")

        li = BeautifulSoup(b.html)
        for show in li.select('td.title > a'):
            url = show.get('href')
            title = show.text
            print("Retrieving " + title)

            b.load(url)

            sh = BeautifulSoup(b.html)
            CSV_url = sh.select('div#servicesList > p > a')[1]['href']

            fi = b.download(BASE_URL + CSV_url)
            lines = fi.splitlines(False)

            # Is there enough data?
            title_row = lines[0]
            if "Item Views" not in title_row or \
                            "Item Clickthroughs" not in title_row or \
                            "Enclosure Downloads" not in title_row:
                # Activate additional statistics for this podcast
                # Using sys.stdout.write to avoid trailing newline (so that "Done!" is on the same line)
                sys.stdout.write("  Telling feedburner to track item views, clickthroughs and downloads... ")
                # Construct URL for settings page
                settings_url = url.replace("dashboard", "analyze/totalstats")
                # Load that page
                b.load(settings_url)
                # Check boxes for collecting item views and click throughs and downloads
                b.wk_check("#itemViews")
                b.wk_check("#clickThroughs")
                b.wk_check("#downloads")
                # Hit the save button
                b.wk_click("div.customizerFooter > p > input", wait_load=True)
                # Redownload CSV (this time with enough columns)
                fi = b.download(BASE_URL + CSV_url)
                lines = fi.splitlines(False)

                print("Done!")

            csv_fi = csv.reader(lines[1:], delimiter=",")

            # Add this show if it's not in the database
            shows = Show.objects.filter(name = title)
            if len(shows) == 0:
                s = Show(name = title, digas_id = "")
                s.save()
            else:
                s = shows[0]

            # First, delete all old objects (bulk_create can't update, only create new)
            PodcastStatistics.objects.filter(show=s).delete()

            rows_to_insert = []
            for row in csv_fi:
                rows_to_insert.append(PodcastStatistics(
                        date = datetime.strptime(row[0], "%m-%d-%Y"),
                        subscribers = row[1],
                        reach = row[2],
                        views = row[3],
                        clickthroughs = row[4],
                        downloads = row[5],
                        hits = row[6],
                        show = s
                        ))

            # Finally, we create all the objects. Far faster than creating one at a time.
            PodcastStatistics.objects.bulk_create(rows_to_insert)

        print "Done."
