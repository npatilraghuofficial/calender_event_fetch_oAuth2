from django.urls import path
from calendar_integration.views import GoogleCalendarInitView, GoogleCalendarRedirectView

urlpatterns = [
   
    path('rest/v1/calendar/init/', GoogleCalendarInitView.as_view(), name='google_calendar_init'),
    path('rest/v1/calendar/redirect/', GoogleCalendarRedirectView.as_view(), name='google_calendar_redirect'),
  
]
