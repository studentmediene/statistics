#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
from datetime import date, datetime
from glob import glob

from django.core.management.base import BaseCommand, CommandError
from podcast.models import Show, PodcastStatistics
from statistics.settings import FEEDBURNER_EMAIL, FEEDBURNER_PASSWORD

import spynner, requests, os, sys, io, csv
from PyQt4.QtCore import Qt
from bs4 import BeautifulSoup

BASE_URL = "http://feedburner.google.com"

class Command(BaseCommand):
    format = "Format: python manage.py retrieve-csvs"
    help = "Retrieve all CSVs from Feedburner. " + format

    def handle(self, *args, **kwargs):
        b = spynner.Browser()
        b.show()
        print("Started...")

        b.load("http://feedburner.google.com")
        print("Loaded Feedburner...")

        b.wk_fill('input[name=Email]', FEEDBURNER_EMAIL)
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
            csv_fi = csv.reader(fi.splitlines(False)[1:], delimiter=",")

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
