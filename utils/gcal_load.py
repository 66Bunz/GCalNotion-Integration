
import datetime


def gcal_load(event, gcal_service, gcal_calendarid, events_db):
    """
    Loads events on Google Calendar.

    Args:
        event:
        gcal_service:
        gcal_calendarid:
        events_db:
    """

    try:
        if bool(datetime.datetime.strptime(event['start'], "%Y-%m-%d")):
            # print('data')

            event_post = {
                'summary': event['title'],
                'start': {
                    'date': event['start'],
                    'timeZone': 'Europe/Rome',
                },
                'end': {
                    'date': event['end'],
                    'timeZone': 'Europe/Rome',
                },
                'description': event['description'],
                # 'colorId': event['color'],
                'location': event['location'],
            }

    except ValueError:
        # print('datetime')
        event_post = {
            'summary': event['title'],
            'start': {
                'dateTime': event['start'],
                'timeZone': 'Europe/Rome',
            },
            'end': {
                'dateTime': event['end'],
                'timeZone': 'Europe/Rome',
            },
            'description': event['description'],
            # 'colorId': event['color'],
            'location': event['location'],
        }

    just_posted_event = gcal_service.events().insert(calendarId=gcal_calendarid, body=event_post).execute()
    print(f'Evento creato su GCal')

    now_utc = datetime.datetime.utcnow()

    # TODO: togliere minLimit e maxLimit e metterli come argomenti in integration.py
    week_decrease_4 = datetime.timedelta(weeks=4)
    minLimit = now_utc - week_decrease_4
    minLimit = minLimit.isoformat() + 'Z'
    # print(minLimit)

    week_add_8 = datetime.timedelta(weeks=8)
    maxLimit = now_utc + week_add_8
    maxLimit = maxLimit.isoformat() + 'Z'

    events_result = gcal_service.events().list(calendarId=gcal_calendarid, timeMin=minLimit, timeMax=maxLimit, maxResults=100, singleEvents=True, orderBy='startTime').execute()
    # print(events_result)
    events = events_result.get('items')

    if not events:
        print('No events found.')

    for event in events:
        gcalID = event['id']
        gcal_updated = event['updated']
        # print(event)
        if just_posted_event['summary'] == event['summary']:
            print('Aggiungendo gcalID sul DB')
            # print(gcalID)
            gcal_event = {
                "gcalID": gcalID,
                "gcal_updated": gcal_updated
            }
            events_db.update_one({'title': just_posted_event['summary']}, {'$set': gcal_event})
            print('gcalID aggiunto sul DB')

        else:
            pass
