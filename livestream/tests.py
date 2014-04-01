from django.test import TestCase

def test1():
    PATH = "/usr/share/icecast2/log/access.log"
    parsed_file = parse_access_log_file(PATH)

    day = datetime(2014, 02, 25)
    for hour in xrange(1,24+1):
        starttime = datetime(day.year, day.month, day.day, hour-1)
        if (hour != 24):
            endtime = datetime(day.year, day.month, day.day, hour)
        else:
            endtime = datetime(day.year, day.month, day.day, 23, 59, 59)

        listeners_in_interval = get_listeners_in_interval(parsed_file, starttime, endtime)
        print("Unique listeners between %d and %d: %d" % (hour-1, hour, len(listeners_in_interval),))

def twitch_plays_pokemon():
    PATH = "/usr/share/icecast2/log/access.log.20140219_221217"
    parsed_file = parse_access_log_file(PATH)

    day = datetime(2014, 02, 18)
    for hour in xrange(13, 24+1):
        starttime = datetime(day.year, day.month, day.day, hour-1)
        if (hour != 24):
            endtime = datetime(day.year, day.month, day.day, hour)
        else:
            endtime = datetime(day.year, day.month, day.day, 23, 59, 59)

        listeners_in_interval = get_listeners_in_interval(parsed_file, starttime, endtime)
        print("Unique listeners between %d and %d: %d" % (hour-1, hour, len(listeners_in_interval),))

    day = datetime(2014, 02, 19)
    for hour in xrange(01, 12+1):
        starttime = datetime(day.year, day.month, day.day, hour-1)
        if (hour != 24):
            endtime = datetime(day.year, day.month, day.day, hour)
        else:
            endtime = datetime(day.year, day.month, day.day, 23, 59, 59)

        listeners_in_interval = get_listeners_in_interval(parsed_file, starttime, endtime)
        print("Unique listeners between %d and %d: %d" % (hour-1, hour, len(listeners_in_interval),))

    starttime = datetime(2014, 02, 18, 21)
    endtime = datetime(2014, 02, 19, 03)
    listeners_in_interval = get_listeners_in_interval(parsed_file, starttime, endtime)
    print("Unique listeners between %d and %d: %d" % (21, 03, len(listeners_in_interval),))
