
import datetime
import requests
from googleapiclient.errors import HttpError

import utils.gcal_load, utils.notion_load


def db_load(gcal_service, gcal_calendarid, notion_headers, notion_database, events_db, max_time=None):
    """
    Loads the events from Google Calendar into the MongoDB database, loads the events from Notion into the MongoDB database, then loads the differences.

    Args:
        gcal_service:
        gcal_calendarid:
        notion_headers:
        notion_database:
        events_db:
        max_time:
    """

    try:
        now_utc_iso = datetime.datetime.utcnow().isoformat() + 'Z'
        # print(now_utc_iso)
        now_utc = datetime.datetime.utcnow()

        week_decrease_4 = datetime.timedelta(weeks=4)
        minLimit = now_utc - week_decrease_4
        minLimit = minLimit.isoformat() + 'Z'
        # print(minLimit)

        week_add_8 = datetime.timedelta(weeks=8)
        maxLimit = now_utc + week_add_8
        maxLimit = maxLimit.isoformat() + 'Z'
        # print(maxLimit)

        print('----Searching events from GCal----')
        events_result = gcal_service.events().list(calendarId=gcal_calendarid, timeMin=minLimit, timeMax=maxLimit, maxResults=10, singleEvents=True, orderBy='startTime').execute()

        events = events_result.get('items')

        if not events:
            print('No upcoming events found from GCal.')
            print('------')
        for event in events:
            gcalID = event['id']
            created = event['created']
            gcal_updated = event['updated']
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            title = event['summary']

            if event.get('description', None):
                description = event['description']
            else:
                description = None
            if event.get('colorId', None):
                color = f"{event['colorId']}"
            else:
                color = None
            if event.get('location', None):
                location = event['location']
            else:
                location = None

            gcal_event = {
                "gcalID": gcalID,
                "notionID": None,
                "created": created,
                "gcal_updated": gcal_updated,
                "notion_updated": None,
                "start": start,
                "end": end,
                "title": title,
                "description": description,
                "color": color,
                "location": location,
                # "reminder": "",
            }

            gcal_event_update = {
                "gcalID": gcalID,
                "created": created,
                "gcal_updated": gcal_updated,
                "start": start,
                "end": end,
                "title": title,
                "description": description,
                "color": color,
                "location": location,
                # "reminder": "",
            }

            print('----')

            if events_db.find_one({'gcalID': gcal_event['gcalID']}) is None:
                events_db.insert_one(gcal_event)
                print(f'Event {title} of {start} added to DB')
            else:
                print(f'Event {title} of {start} was already saved in DB')

                print('\nChecking if there are updates on GCal')

                if gcal_updated != events_db.find_one({'gcalID': gcal_event['gcalID']})['gcal_updated']:

                    events_db.update_one({'gcalID': gcal_event['gcalID']}, {'$set': gcal_event_update})
                    print(f'{title} was updated on DB')
                    updated_event = events_db.find_one({'gcalID': gcal_event['gcalID']})
                    gcalId = updated_event['gcalID']
                    notionId = updated_event['notionID']
                    utils.gcal_patch(updated_event, gcal_service, gcal_calendarid, gcalId)
                    utils.notion_patch(updated_event, notion_headers, notion_database, notionId)

                else:
                    print(f'{title} is up to date on the DB')

                print('------')

    except HttpError as error:
        print(f'An error occurred: {error}')

        print('------')

    notion_read_url = f"https://api.notion.com/v1/databases/{notion_database}/query"

    # TODO: fare filtro temporale con variabile
    filters = {
        "page_size": 100,
        "filter": {
            "property": "title",
            "rich_text": {"is_not_empty": True}
        }
    }

    try:
        print('----Searching events from Notion----')
        response = requests.post(notion_read_url, json=filters, headers=notion_headers)
        response.raise_for_status()
        events = response.json()['results']

        if not events:
            print('No upcoming events found from Notion.')
            print('------')

        for event in events:

            notionID = event['id']
            created = event['created_time']
            notion_updated = event['last_edited_time']
            date = event['properties']['Data']['date']
            start = date['start']
            if date['end'] is None:
                end = start
            else:
                end = date['end']

            title = event['properties']['Nome']['title'][0]['text']['content']

            if event['properties']['Descrizione']['rich_text']:
                description = event['properties']['Descrizione']['rich_text'][0]['text']['content']
            else:
                description = None
            if event['properties']['Tag']['select']:
                color = event['properties']['Tag']['select']['color']
            else:
                color = None
            if event['properties']['Posizione']['rich_text']:
                location = event['properties']['Posizione']['rich_text'][0]['text']['content']
            else:
                location = None

            notion_event = {
                "gcalID": None,
                "notionID": notionID,
                "created": created,
                "gcal_updated": None,
                "notion_updated": notion_updated,
                "start": start,
                "end": end,
                "title": title,
                "description": description,
                "color": color,
                "location": location,
                # "reminder": "",
            }

            notion_event_update = {
                "notionID": notionID,
                "created": created,
                "notion_updated": notion_updated,
                "start": start,
                "end": end,
                "title": title,
                "description": description,
                "color": color,
                "location": location,
                # "reminder": "",
            }

            print('----')

            if events_db.find_one({'notionID': notion_event['notionID']}) is None:
                events_db.insert_one(notion_event)
                print(f'Event {title} of {start} added to DB')
            else:
                print(f'Event {title} of {start} was already saved in DB')
                print('\nChecking if there are updates on Notion')

                if notion_updated != events_db.find_one({'notionID': notion_event['notionID']})['notion_updated']:
                    print(f'{title} was updated on the DB')
                    events_db.update_one({'notionID': notion_event['notionID']}, {'$set': notion_event_update})
                    updated_event = events_db.find_one({'notionID': notion_event['notionID']})
                    gcalId = updated_event['gcalID']
                    notionId = updated_event['notionID']
                    utils.gcal_patch(updated_event, gcal_service, gcal_calendarid, gcalId)
                    utils.notion_patch(updated_event, notion_headers, notion_database, notionId)

                else:
                    print(f'{title} is up to date on the DB')

            print('------')

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as error:
        print(f'An error occurred: {error}')
        print('------')

    for event in events_db.find():
        if event['gcalID'] is None:
            print('gcal_post')
            utils.gcal_load(event, gcal_service, gcal_calendarid, events_db)

        elif event['notionID'] is None:
            print('notion_post')
            utils.notion_load(event, notion_headers, notion_database, events_db)
