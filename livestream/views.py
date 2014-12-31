# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.shortcuts import render
from django.http import HttpResponse

from livestream.models import PeriodSummary, StreamListeners
from livestream.util import get_last_broadcasts, get_total_listeners_per_show, get_show_in_period, get_stream_listeners_from_api, is_rebroadcast

##### HTML views

def show(request, show):
    last_broadcasts = get_last_broadcasts()
    total_show_listeners = get_total_listeners_per_show(months=3)

    all_recent_broadcasts = PeriodSummary.objects.filter(
                endtime__gte=(datetime.today() - timedelta(5*365/12)),
                show_in_period__icontains=show
            ).order_by('-endtime')

    rebroadcasts = [b for b in all_recent_broadcasts if is_rebroadcast(b.show_in_period)]
    live_broadcasts = [b for b in all_recent_broadcasts if not is_rebroadcast(b.show_in_period)]

    return render(request, 'show.html', { "show": show, "live_broadcasts": live_broadcasts, "rebroadcasts": rebroadcasts, "last_broadcasts": last_broadcasts, "total_show_listeners": total_show_listeners })

def overview(request):
    last_broadcasts = get_last_broadcasts()
    total_show_listeners = get_total_listeners_per_show(months=3)

    record = StreamListeners.objects.order_by('-listeners')[0]
    record_context = {"listeners": record.listeners,
            "datetime": record.datetime,
            "show": get_show_in_period(record.datetime)}

    return render(request, 'overview.html', {"last_broadcasts": last_broadcasts, "record": record_context, "total_show_listeners": total_show_listeners})

##### API views

def stream_listeners(request):
    """Serves the number of stream listeners at the
    current instant for AJAX use."""
    (total_listeners, _, _, _) = get_stream_listeners_from_api()
    return HttpResponse(total_listeners)
