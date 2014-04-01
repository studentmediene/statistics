from django.db import models

class LogEntry(models.Model):
    IP = models.CharField(max_length=50)
    datetime_end = models.DateTimeField()
    datetime_start = models.DateTimeField()
    http_request = models.TextField()
    http_status = models.CharField(max_length=20)
    http_bytes = models.IntegerField()
    http_referer = models.TextField()
    http_agent = models.TextField()
    duration = models.IntegerField()

    class Meta:
        verbose_name = "log entry"
        verbose_name_plural = "log entries"

class StreamListeners(models.Model):
    listeners = models.IntegerField()
    datetime = models.DateTimeField(unique=True)
    IPs = models.TextField(blank=True) # JSON
    seconds_connected = models.TextField(blank=True) # JSON
    user_agents = models.TextField(blank=True) # JSON
    stream = models.CharField(max_length=100)

    def __unicode__(self):
        return "StreamListeners: %d listeners at %s" % (self.listeners, self.datetime.isoformat(),)

    class Meta:
        verbose_name = "stream listeners"
        verbose_name_plural = "stream listeners"

class PeriodSummary(models.Model):
    unique_listeners = models.IntegerField()
    listener_info = models.TextField() # JSON
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    show_in_period = models.CharField(max_length=255)

    def __unicode__(self):
        return "PeriodSummary: %s to %s" % (self.starttime.isoformat(), self.endtime.isoformat(),)

    class Meta:
        unique_together = ('starttime', 'endtime',)
        verbose_name = "period summary"
        verbose_name_plural = "period summaries"
