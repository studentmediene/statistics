from django.test import TestCase

def test1():
    PATH = "/usr/share/icecast2/log/access.log"
    parsed_file = parse_access_log_file(PATH)

    day = datetime(2014, 0o2, 25)
    for hour in range(1,24+1):
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

    day = datetime(2014, 0o2, 18)
    for hour in range(13, 24+1):
        starttime = datetime(day.year, day.month, day.day, hour-1)
        if (hour != 24):
            endtime = datetime(day.year, day.month, day.day, hour)
        else:
            endtime = datetime(day.year, day.month, day.day, 23, 59, 59)

        listeners_in_interval = get_listeners_in_interval(parsed_file, starttime, endtime)
        print("Unique listeners between %d and %d: %d" % (hour-1, hour, len(listeners_in_interval),))

    day = datetime(2014, 0o2, 19)
    for hour in range(0o1, 12+1):
        starttime = datetime(day.year, day.month, day.day, hour-1)
        if (hour != 24):
            endtime = datetime(day.year, day.month, day.day, hour)
        else:
            endtime = datetime(day.year, day.month, day.day, 23, 59, 59)

        listeners_in_interval = get_listeners_in_interval(parsed_file, starttime, endtime)
        print("Unique listeners between %d and %d: %d" % (hour-1, hour, len(listeners_in_interval),))

    starttime = datetime(2014, 0o2, 18, 21)
    endtime = datetime(2014, 0o2, 19, 0o3)
    listeners_in_interval = get_listeners_in_interval(parsed_file, starttime, endtime)
    print("Unique listeners between %d and %d: %d" % (21, 0o3, len(listeners_in_interval),))
