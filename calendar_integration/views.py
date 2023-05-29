import json
import os

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.views import View
from google_auth_oauthlib.flow import Flow
from calendar_integration.models import CalendarEvent
import googleapiclient.discovery


class GoogleCalendarInitView(View):
    def get(self, request):
        my_secret = os.environ['GOOGLE_CLIENT_SECRET_FILE']
        client_secret_data = json.loads(my_secret)
        flow = Flow.from_client_config(
            client_secret_data,
            scopes=['https://www.googleapis.com/auth/calendar.events.readonly'],
            redirect_uri=request.build_absolute_uri('/rest/v1/calendar/redirect/')
        )
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        request.session['oauth2_state'] = state
        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        if 'code' not in request.GET or 'oauth2_state' not in request.session:
            return HttpResponse('Authorization failed.')

        my_secret = os.environ['GOOGLE_CLIENT_SECRET_FILE']
        client_secret_data = json.loads(my_secret)
        flow = Flow.from_client_config(
            client_secret_data,
            scopes=['https://www.googleapis.com/auth/calendar.events.readonly'],
            redirect_uri=request.build_absolute_uri('/rest/v1/calendar/redirect/')
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri(), state=request.session['oauth2_state'])
        credentials = flow.credentials

        access_token = credentials.token
        service = googleapiclient.discovery.build(
            serviceName='calendar',
            version='v3',
            credentials=credentials,
            discoveryServiceUrl='https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest',
            cache_discovery=False
        )
        events = service.events().list(calendarId='primary').execute()

        event_list = []
        for event in events.get('items', []):
            event_data = {
                'event_id': event['id'],
                'summary': event['summary'],
                'start_time': event['start'].get('dateTime'),
                'end_time': event['end'].get('dateTime')
            }
            event_list.append(event_data)
            calendar_event = CalendarEvent(
                event_id=event['id'],
                summary=event['summary'],
                start_time=event['start'].get('dateTime'),
                end_time=event['end'].get('dateTime')
            )
            calendar_event.save()

        return JsonResponse(event_list, safe=False)
