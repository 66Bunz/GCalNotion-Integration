
import datetime
import sys


def gcal_load(event, gcal_service, gcal_calendarid, events_db, limits):
    """
    Loads events on Google Calendar.

    Args:
        event:
        gcal_service:
        gcal_calendarid:
        events_db:
        limits:
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

    if limits == 'OneMin':
        # print("OneMin")
        week_decrease = datetime.timedelta(weeks=1)
        minLimit = now_utc - week_decrease
        minLimit = minLimit.isoformat() + 'Z'

        week_add = datetime.timedelta(weeks=1)
        maxLimit = now_utc + week_add
        maxLimit = maxLimit.isoformat() + 'Z'

    elif limits == 'FiveMin':
        # print("FiveMin")
        week_decrease = datetime.timedelta(weeks=2)
        minLimit = now_utc - week_decrease
        minLimit = minLimit.isoformat() + 'Z'

        week_add = datetime.timedelta(weeks=3)
        maxLimit = now_utc + week_add
        maxLimit = maxLimit.isoformat() + 'Z'

    elif limits == 'TwentyMin':
        # print("TwentyMin")
        week_decrease = datetime.timedelta(weeks=4)
        minLimit = now_utc - week_decrease
        minLimit = minLimit.isoformat() + 'Z'

        week_add = datetime.timedelta(weeks=8)
        maxLimit = now_utc + week_add
        maxLimit = maxLimit.isoformat() + 'Z'

    else:
        print(f'Error, limits parameter gave an unexpected value: {limits}')
        sys.exit()

    events_result = gcal_service.events().list(calendarId=gcal_calendarid, timeMin=minLimit, timeMax=maxLimit,  maxResults=100).execute()
    events = events_result.get('items')

    if not events:
        print('No events found.')

    for event in events:
        gcalID = event['id']
        gcal_updated = event['updated']
        if just_posted_event['summary'] == event['summary']:
            print('Aggiungendo gcalID sul DB')

            events_db.update_one({'title': just_posted_event['summary']}, {'$set': {
                "gcalID": gcalID,
                "gcal_updated": gcal_updated
            }})
            print('gcalID aggiunto sul DB')

        else:
            pass
