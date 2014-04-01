from django.db import models

class OndemandBroadcastStatistics(models.Model):
    """Statistics for one given broadcast."""
    show = models.ForeignKey('podcast.Show')
    broadcast = models.CharField(max_length=10)

    pageviews = models.IntegerField()
    unique_pageviews = models.IntegerField()

class OndemandPeriodStatistics(models.Model):
    """Stream on demand statistics for a
    given period."""
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    show = models.ForeignKey('podcast.Show')

    # Statistics for all pages, including
    # broadcast lists and the front page
    total_pageviews = models.IntegerField()
    total_unique_pageviews = models.IntegerField()

    # Statistics for broadcasts only
    broadcast_pageviews = models.IntegerField()
    broadcast_unique_pageviews = models.IntegerField()
