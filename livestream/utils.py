from datetime import datetime

from django.db import IntegrityError

from statistics.settings import ICECAST2_MOUNTPOINT
from livestream.models import StreamListeners

def import_current_listener_history():
    """Imports number of current listeners at
    datetime from the old flat file format.
    
    Example: 2014-02-19-03:05:03;8##Garasjen"""
    sl = []
    with open("listeners_log.txt") as log:
        for line in log:
            (dt_string, remainder) = line.split(";")
            dt = datetime.strptime(dt_string, "%Y-%m-%d-%H:%M:%S")
            (listeners, show) = remainder.split("##")
            sl.append(StreamListeners(listeners=int(listeners), datetime=dt, stream=ICECAST2_MOUNTPOINT))
    for s in sl:
        try:
            s.save()
        except IntegrityError as e:
            print("Could not save entry for %s:" % (s.datetime.isoformat(),))
            print(str(e))

