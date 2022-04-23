
import datetime


def gcal_patch(updated_event, gcal_service, gcal_calendarid, eventId):
    """
    Patches events on Google Calendar.

    Args:
        updated_event:
        gcal_service:
        gcal_calendarid:
        eventId:
    """

    print('GCAL PATCH')

    try:
        if bool(datetime.datetime.strptime(updated_event['start'], "%Y-%m-%d")):

            event_patch = {
                'summary': updated_event['title'],
                'start': {
                    'date': updated_event['start'],
                    'timeZone': 'Europe/Rome',
                },
                'end': {
                    'date': updated_event['end'],
                    'timeZone': 'Europe/Rome',
                },
                'description': updated_event['description'],
                # 'colorId': event['color'],
                'location': updated_event['location'],
            }

    except ValueError:
        event_patch = {
            'summary': updated_event['title'],
            'start': {
                'dateTime': updated_event['start'],
                'timeZone': 'Europe/Rome',
            },
            'end': {
                'dateTime': updated_event['end'],
                'timeZone': 'Europe/Rome',
            },
            'description': updated_event['description'],
            # 'colorId': event['color'],
            'location': updated_event['location'],
        }

    gcal_service.events().patch(calendarId=gcal_calendarid, eventId=eventId, body=event_patch,).execute()
    print(f'Evento aggiornato su GCal')
