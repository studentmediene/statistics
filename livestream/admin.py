from django.contrib import admin
from livestream.models import LogEntry, PeriodSummary, StreamListeners

admin.site.register(LogEntry)
admin.site.register(PeriodSummary)
admin.site.register(StreamListeners)
