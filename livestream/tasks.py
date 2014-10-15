from __future__ import absolute_import
import json
import urllib2
from datetime import datetime, timedelta
from copy import deepcopy

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab

from livestream.views import load_correct_access_log_files, get_listeners_in_interval, get_stream_listeners_from_api, load_and_merge_files
from livestream.parse import parse_access_log
from livestream.models import PeriodSummary, StreamListeners

from statistics.celery import app
from statistics.settings import SHOW_NAME_API, BASE_DIR

def prepare_listener_info(info_):
    """Prepares listener_info for JSON
    serialization by converting the
    datetimes to strings."""
    info = deepcopy(info_)
    for i, listener in enumerate(info):
        info[i]["datetime_end"] = info[i]["datetime_end"].isoformat()
        info[i]["datetime_start"] = info[i]["datetime_start"].isoformat()
    return info

def get_show_in_period(starttime, endtime=None):
    """Retrieves the show in the given period
    from the radio API."""
    url = SHOW_NAME_API % (starttime.year, starttime.month, starttime.day,)

    a = urllib2.urlopen(url)
    show_json = json.load(a)
    for show in show_json:
        if datetime.strptime(show["starttime"], "%Y-%m-%d %H:%M:%S").hour == starttime.hour:
            return show["title"]
        elif datetime.strptime(show["starttime"], "%Y-%m-%d %H:%M:%S") <= starttime < datetime.strptime(show["endtime"], "%Y-%m-%d %H:%M:%S"):
            return show["title"]
    return "Ukjent"

@periodic_task(run_every=crontab(minute='*/1'))
def insert_current_listeners():
    """Inserts the current number of stream listeners into
    the StreamListeners table."""
    (total_listeners, IPs, seconds_connected, user_agents) = get_stream_listeners_from_api()
    json_IPs = json.dumps(IPs)
    json_seconds_connected = json.dumps(seconds_connected)
    json_user_agents = json.dumps(user_agents)
    now = datetime.now()
    listeners = StreamListeners(listeners=int(total_listeners), datetime=now, IPs=json_IPs,
            seconds_connected=json_seconds_connected, user_agents=json_user_agents, stream=ICECAST2_MOUNTPOINT)
    listeners.save()

@periodic_task(run_every=crontab(minute='*/3'))
def update_recent_shows():
    """Inserts or updates the number of unique stream
    listeners for a time slot into the PeriodSummary table."""
    now = datetime.now()
    last_full_hour = datetime(now.year, now.month, now.day, now.hour)

    starttime = last_full_hour - timedelta(hours=12)
    endtime = last_full_hour

    file_names = load_correct_access_log_files(starttime, endtime)
    lines = load_and_merge_files(file_names)
    parsed_file = parse_access_log(lines)

    for t in range(12):
        _starttime = endtime - timedelta(hours=t+1)
        _endtime = endtime - timedelta(hours=t)
        (unique_listeners, listeners_in_interval) = get_listeners_in_interval(parsed_file, _starttime, _endtime)
        show_info = {"starttime": _starttime,
            "endtime": _endtime,
            "listeners": len(unique_listeners),
            "listener_info": unique_listeners,
            "name": get_show_in_period(_starttime, _endtime),
            }
        try:
            hour_summary = PeriodSummary.objects.get(starttime=_starttime, endtime=_endtime)
            hour_summary.listener_info = json.dumps(prepare_listener_info(show_info["listener_info"]))
            hour_summary.unique_listeners = show_info["listeners"]
            hour_summary.show_in_period = show_info["name"]
        except PeriodSummary.DoesNotExist:
            hour_summary = PeriodSummary(unique_listeners=show_info["listeners"],
                    starttime=show_info["starttime"],
                    endtime=show_info["endtime"],
                    show_in_period=show_info["name"],)
        hour_summary.save()

@periodic_task(run_every=crontab(minute='*/15'))
def create_plots():
    """Creates plots for number of unique listeners per time slot
    over the last day and week."""
    import os
    from matplotlib import use
    use('Agg')
    import tempfile
    import matplotlib
    import matplotlib.pyplot as pl
    import matplotlib.mlab as ml
    import numpy as np
    from shutil import copyfile

    smoothing = 0.2

    period_summaries = PeriodSummary.objects.order_by('-endtime')
    last_day = map(lambda s: (s.unique_listeners, s.starttime), period_summaries[0:23])

    if len(period_summaries) > 168:
        last_week = period_summaries[0:167]
    else:
        last_week = period_summaries[0:]
    last_week = map(lambda s: (s.unique_listeners, s.starttime + timedelta(minutes=30)), last_week)

    ############
    ### Last day
    ld_zipped = zip(*last_day)
    ld_listeners = ld_zipped[0]
    ld_times = matplotlib.dates.date2num(ld_zipped[1])

    locator = matplotlib.dates.HourLocator()
    formatter = matplotlib.dates.DateFormatter('%H:%M')

    fig = pl.figure(figsize=(20,4))
    ax = pl.subplot(111)
    ax.tick_params(labelsize=10, color=(0.45, 0.45, 0.45), labelcolor=(0.45, 0.45, 0.45))
    for spine in ax.spines.values():
        spine.set_edgecolor((0.45, 0.45, 0.45))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.bar(ld_times, ld_listeners, width=1.0/24.0, color=(0.75, 0.75, 0.75))
    ax.xaxis_date()
    fig.autofmt_xdate()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    pl.tick_params(labelsize=10)
    pl.show()
    pl.ylim(0, pl.ylim()[1])
	
    pl.savefig(os.path.join(BASE_DIR, 'static', 'img', 'last_day.png'), dpi=125, bbox_inches='tight')

    #############
    ### Last week
    lw_zipped = zip(*last_week)
    lw_listeners = lw_zipped[0]
    lw_times = matplotlib.dates.date2num(lw_zipped[1])

    l_avg = [0]*len(lw_times)
    l_avg[0] = int(lw_listeners[0])

    for i in range(1, len(lw_times)):
        l_avg[i] = smoothing*int(lw_listeners[i-1]) + (1-smoothing)*l_avg[i-1]

    fig = pl.figure(figsize=(20,4))
    ax = pl.subplot(111)
    ax.tick_params(labelsize=10, color=(0.45, 0.45, 0.45), labelcolor=(0.45, 0.45, 0.45))
    for spine in ax.spines.values():
        spine.set_edgecolor((0.45, 0.45, 0.45))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    pl.plot_date(lw_times, l_avg, 'b-', color=(0.75, 0.75, 0.75))
    fig.autofmt_xdate()
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    pl.tick_params(labelsize=10)
    pl.show()
    pl.ylim(0, pl.ylim()[1])
	
    pl.savefig(os.path.join(BASE_DIR, 'static', 'img', 'last_week.png'), dpi=125, bbox_inches='tight')
