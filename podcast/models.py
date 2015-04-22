from django.db import models

class PodcastStatistics(models.Model):
    """Podcast statistics for a given show
    and date."""
    date = models.DateTimeField()
    subscribers = models.IntegerField()
    reach = models.IntegerField()
    views = models.IntegerField()
    clickthroughs = models.IntegerField()
    downloads = models.IntegerField()
    hits = models.IntegerField()

    show = models.ForeignKey('podcast.Show')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "podcast listeners"
        verbose_name_plural = "podcast listeners"

    def __unicode__(self):
        return "%s (%s)" % (self.show, self.date,)

class Show(models.Model):
    """Common show class for podcast and ondemand."""
    name = models.CharField(max_length=255)
    digas_id = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name
