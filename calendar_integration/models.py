from django.db import models

class CalendarEvent(models.Model):
    event_id = models.CharField(max_length=100)
    summary = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
 