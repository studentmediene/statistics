from datetime import datetime, timedelta

from django.shortcuts import render

from livestream import parse
from livestream.models import PeriodSummary, StreamListeners
from livestream.tasks import get_show_in_period

from statistics.settings import BRAND_NAME

def frontpage(request):
    context_settings = {"BRAND_NAME": BRAND_NAME}

    try:
        last_shows = PeriodSummary.objects.order_by('-endtime')[0:12]
    except IndexError:
        last_shows = {}

    record = StreamListeners.objects.order_by('-listeners')[0]
    record_context = {"listeners": record.listeners,
            "datetime": record.datetime,
            "show": get_show_in_period(record.datetime)}

    return render(request, 'index.html',
            {"last_shows": last_shows,
                "record": record_context,
                "settings": context_settings,
                })
