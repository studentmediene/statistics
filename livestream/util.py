# -*- coding: utf-8 -*-
import urllib2
import os
import json
from copy import deepcopy
from sys import argv
from bs4 import BeautifulSoup

from statistics.settings import LIVESTREAM_LOG_PATH, BASE_DIR, DEBUG, ICECAST2_USER, ICECAST2_PASS, ICECAST2_MOUNTPOINT, ICECAST2_ROOT, SHOW_NAME_API
from datetime import date, datetime, timedelta
from glob import glob

from livestream.models import PeriodSummary, StreamListeners

def get_last_broadcasts():
    try:
        return PeriodSummary.objects.order_by('-endtime')[0:30]
    except IndexError:
        return {}

def get_total_listeners_per_show(months):
    try:
        all_recent_broadcasts = PeriodSummary.objects.filter(endtime__gte=(datetime.today() - timedelta(months*365/12))).order_by('-endtime')

        show_listeners_dict = {}
        for broadcast in all_recent_broadcasts:
            show_name = broadcast.show_in_period
            canonical_name = show_name.rsplit("(")[0].rstrip().title()
            is_rebroadcast = True if "(R)" in show_name or "(R2)" in show_name or "(R3)" in show_name else False

            if canonical_name not in show_listeners_dict:
                show_listeners_dict[canonical_name] = [0, 0]

            # { showname: [ordinary_listeners, rebroadcast_listeners] }
            if is_rebroadcast:
                show_listeners_dict[canonical_name][1] += broadcast.unique_listeners
            else:
                show_listeners_dict[canonical_name][0] += broadcast.unique_listeners

        return sorted(show_listeners_dict.items(), key=lambda x: -x[1][0])
    except IndexError:
        return {}

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

def get_stream_listeners_from_api():
    """Retrieves the numbers of stream listeners at the
    current instant from the API, and removes blacklisted
    IPs."""
    p = urllib2.HTTPPasswordMgrWithDefaultRealm()
    p.add_password(None, ICECAST2_ROOT + '/admin/', ICECAST2_USER, ICECAST2_PASS)
    auth_handler = urllib2.HTTPBasicAuthHandler(p)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
    a = urllib2.urlopen(ICECAST2_ROOT + '/admin/listclients.xsl?mount=/' + ICECAST2_MOUNTPOINT).read()

    blacklist = load_blacklist()

    s = BeautifulSoup(a)
    parent = s.find("table", {"id": "listenertable"})

    total_listeners = 0
    IPs = []
    seconds_connected = []
    user_agents = []

    for i, child in enumerate(parent.children):
        if i == 0:
            # Title row
            continue
        ip = child.contents[0].contents[0]
        _seconds_connected = child.contents[1].contents[0]
        full_agent = child.contents[3].contents[0]
        short_agent = full_agent.split("/")[0] # We don't care about version numbers and OS
        if (ip not in blacklist) and (short_agent not in blacklist):
            total_listeners += 1
            IPs.append(ip)
            seconds_connected.append(_seconds_connected)
            user_agents.append(full_agent)
    
    return (total_listeners, IPs, seconds_connected, user_agents)

def load_blacklist():
    """The blacklist contains a list of known bots
    and other IPs that should not be included in the
    statistics."""
    blacklist = set()
    with open(os.path.join(BASE_DIR, "livestream", "blacklist.txt")) as blacklist_file:
        for line in blacklist_file:
            blacklist.add(line[:-1])
    return blacklist

def get_listeners_in_interval(listeners, starttime, endtime):
    """Generates a list of unique listeners within a certain
    time interval. To be included, a listener must have
    listened to the stream for at least 10 seconds."""

    listeners_in_interval = []
    unique_listeners = []
    seen_ips = set()

    # FIXME: Mer fornuftig måte å løse dette på
    for listener in listeners:
        if listener["duration"] > 10:
            if (starttime <= listener["datetime_start"] <= endtime) or (starttime <= listener["datetime_end"] <= endtime) or ((listener["datetime_start"] < starttime) and (listener["datetime_end"] > endtime)):
                if listener["ip"] not in seen_ips:
                    unique_listeners.append(listener)
                    seen_ips.add(listener["ip"])
                else:
                    listeners_in_interval.append(listener)

    return (unique_listeners, listeners_in_interval)

def get_total_listening_time(listeners_in_interval):
    # Not accurate for short intervals, as
    # it is not taken into account that
    # the listener may have listened for a long time
    # before or after the given interval began or ended.
    return sum(x["duration"] for x in listeners_in_interval)

def get_average_listening_time(listeners_in_interval):
    # Not accurate for short intervals.
    return get_total_listening_time(listeners_in_interval)/len(listeners_in_interval)

def load_and_merge_files(file_names):
    """Returns a list of the lines of every file specified
    by file_names."""
    if DEBUG: print "Merging " + str(len(file_names)) + " files..."
    blacklist = load_blacklist()
    merged_lines = []

    def string_contains_list(string, li):
        """Utility function that checks whether any of the elements in li
        are contained in string."""
        for l in li:
            if l in string:
                return True
        return False

    for fn in file_names:
        with open(fn) as f:
            for line in f:
                # Add line to merged_lines unless
                # the line contains a blacklisted
                # IP, and only if it contains the
                # name of the relevant mount.
                if (ICECAST2_MOUNTPOINT in line) and (not string_contains_list(line, blacklist)):
                    merged_lines.append(line)
    if DEBUG: print str(len(merged_lines)) +  " lines in total."
    return merged_lines

def load_correct_access_log_files(starttime, endtime):
    """Selects the file containing the log entries
    for the given start and end times."""
    files = glob(LIVESTREAM_LOG_PATH + "access.log.*_*")
    # Parse datetimes from the end of the file names
    file_tuples = []
    for f in files:
        f_datetime_fragment = f[-15:]
        file_tuples.append( (f, datetime.strptime(f_datetime_fragment, "%Y%m%d_%H%M%S")) ) # For instance "20130131_114615"
    file_tuples = sorted(file_tuples, key=lambda x: x[1])
    file_dicts = []
    # Collect filenames, starttimes and endtimes
    for i, f in enumerate(file_tuples):
        if i == 0:
            f_starttime = datetime(1950, 1, 1)
        else:
            f_starttime = file_tuples[i-1][1]
        file_dicts.append({"filename": f[0],
                "starttime": f_starttime,
                "endtime": f[1]})
    # Add current access.log file
    file_dicts.append({"filename": LIVESTREAM_LOG_PATH + "access.log", "starttime": file_dicts[-1]["endtime"], "endtime": datetime(2050, 1, 1)})
    # Find file that contains log entries for starttime and hopefully endtime
    file_names = []
    for f in file_dicts:
        if f["starttime"] < endtime < f["endtime"]:
            file_names.append(f["filename"])
            return file_names
        elif f["starttime"] < starttime < f["endtime"]:
            file_names.append(f["filename"])
        elif file_names:
            file_names.append(f["filename"])
    raise ValueError("No file found for given start and end times")
