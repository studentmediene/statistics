from datetime import datetime, timedelta

from django.shortcuts import render

from livestream import parse
from livestream.models import PeriodSummary, StreamListeners
from livestream.tasks import get_show_in_period

def frontpage(request):
    try:
        last_shows = PeriodSummary.objects.order_by('-endtime')[0:30]
    except IndexError:
        last_shows = {}

    try:
        #all_recent_shows = PeriodSummary.objects.order_by('-endtime')[0:3000]
        all_recent_shows = PeriodSummary.objects.filter(endtime__gte=(datetime.today() - timedelta(3*365/12))).order_by('-endtime')

        show_listeners_dict = {}
        for show in all_recent_shows:
            show_name = show.show_in_period
            canonical_name = show_name.rsplit("(")[0].rstrip().title()
            is_rebroadcast = True if "(R)" in show_name or "(R2)" in show_name else False

            if canonical_name not in show_listeners_dict:
                show_listeners_dict[canonical_name] = [0, 0]

            # { showname: [ordinary_listeners, rebroadcast_listeners]
            if is_rebroadcast:
                show_listeners_dict[canonical_name][1] += show.unique_listeners
            else:
                show_listeners_dict[canonical_name][0] += show.unique_listeners

        total_show_listeners = sorted(show_listeners_dict.items(), key=lambda x: -x[1][0])
    except IndexError:
        total_show_listeners = {}

    record = StreamListeners.objects.order_by('-listeners')[0]
    record_context = {"listeners": record.listeners,
            "datetime": record.datetime,
            "show": get_show_in_period(record.datetime)}

    return render(request, 'index.html', {"last_shows": last_shows, "record": record_context, "total_show_listeners": total_show_listeners})
