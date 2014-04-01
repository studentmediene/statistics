from __future__ import absolute_import
import json
import urllib2
from datetime import datetime, timedelta
from copy import deepcopy

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab

from statistics.celery import app
from statistics.settings import SHOW_NAME_API, BASE_DIR

@periodic_task(run_every=crontab(minute='*/1'))
def update_ondemand_statistics():
    pass
