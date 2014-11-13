from datetime import datetime, timedelta

from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from podcast.models import PodcastStatistics, Show

SPRING_SEMESTER_MONTH_START = 1
SPRING_SEMESTER_DAY_START = 1

FALL_SEMESTER_MONTH_START = 8
FALL_SEMESTER_DAY_START = 1

def get_current_semester_start_date():
    now = datetime.now()
    if now.month >= 8:
        return datetime(now.year, FALL_SEMESTER_MONTH_START, FALL_SEMESTER_DAY_START)
    else:
        return datetime(now.year, SPRING_SEMESTER_MONTH_START, SPRING_SEMESTER_DAY_START)

def podcast(request):
    shows = Show.objects.all()
    show_info = []

    for show in shows:
        show_dict = {"name": show.name}
        stat_rows = cache.add('fullstats' + show.name, PodcastStatistics.objects.filter(show = show), 60*60*12)
        stat_rows = cache.get('fullstats' + show.name)

        if len(stat_rows) == 0:
            continue

        #show_dict["last_week"] = stat_rows.filter(date__gte = datetime.now() - timedelta(days=7))
        #show_dict["last_30_days"] = stat_rows.filter(date__gte = datetime.now() - timedelta(days=30))
        #show_dict["this_semester"] = stat_rows.filter(date__gte = get_current_semester_start_date())
        #show_dict["all_time"] = stat_rows

        show_dict["last_week"] = reduce(lambda x, y: x + int(y.downloads), [r for r in stat_rows if r.date >= datetime.now() - timedelta(days=7)], 0)
        show_dict["last_30_days"] = reduce(lambda x, y: x + int(y.downloads), [r for r in stat_rows if r.date >= datetime.now() - timedelta(days=30)], 0)
        show_dict["this_semester"] = reduce(lambda x, y: x + int(y.downloads), [r for r in stat_rows if r.date >= get_current_semester_start_date()], 0)
        show_dict["all_time"] = reduce(lambda x, y: x + int(y.downloads), stat_rows, 0)

        show_dict["first_added"] = stat_rows[0].date.strftime("%Y-%m-%d")

        show_info.append(show_dict)

    shows_sorted_30_days = sorted([(show["name"], show["last_30_days"]) for show in show_info], key=lambda s: int(s[1]), reverse=True)
    shows_sorted_all_time = sorted([(show["name"], show["all_time"]) for show in show_info], key=lambda s: int(s[1]), reverse=True)

    return render(request, 'podcast.html', {"shows": show_info, "30_days_top": shows_sorted_30_days, "all_time_top": shows_sorted_all_time})
