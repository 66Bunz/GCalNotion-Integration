
import requests
import datetime

import os
import pymongo
from pymongo import MongoClient


def db_delete(gcal_service, gcal_calendarid, notion_headers, events_db):
    """
    Deletes events on the database and from the calendars.

    Args:
       gcal_service:
       gcal_calendarid:
       notion_headers:
       events_db:
    """


    cluster = MongoClient(os.environ['mongodb_link'])
    db_cluster = cluster[os.environ['db_cluster']]
    events_db = db_cluster[os.environ['event_db']]
		
    for event in events_db.find():
        print('Checking if events were deleted')
        gcal_id = event['gcalID']
        notion_id = event['notionID']
        check_notion = True

        read_url = f"https://api.notion.com/v1/pages/{notion_id}"

        gcal_event = gcal_service.events().get(calendarId=gcal_calendarid, eventId=event['gcalID']).execute()

        if gcal_event['status'] == 'cancelled':
            event_patch = {
                "archived": True
            }
            requests.request("PATCH", read_url, json=event_patch, headers=notion_headers)
            events_db.delete_one({"gcalID": gcal_id})
            print(f"{event['title']} was deteled in GCal, so {event['title']} was deleted from Notion and database too.")
            check_notion = False
        elif gcal_event['status'] == 'confirmed':
            print("No event was deleted from GCal.")
        else:
            print(f'Error: {gcal_event}')

        # -----------------------------------------------------------------------

        response = requests.request("GET", read_url, headers=notion_headers)
        print(response)

        if check_notion:
            if response.json()['archived'] == True:
                gcal_service.events().delete(calendarId=gcal_calendarid, eventId=gcal_id).execute()
                events_db.delete_one({"notionID": notion_id})
                print(f"{event['title']} was deteled in Notion, so {event['title']} was deleted from GCal and database too.")
            elif response.json()['archived'] == False:
                print("No event was deleted from Notion.")
            else:
                print(f'Error: {response.text}')
        else:
            print('Already deleted from Notion')

        now_utc = datetime.datetime.utcnow()
        week_decrease = datetime.timedelta(weeks=7)
        minLimit = now_utc - week_decrease
        minLimit = minLimit.isoformat() + 'Z'

        if event['end'] < minLimit:
            print(f"{event['title']} was more than 7 weeks old, so it was deleted from the database and it won't be updated anymore on Google Calendar or in Notion.")
            events_db.delete_one({"gcalID": gcal_id})
        else:
            print(f"{event['title']} is less than 7 weeks old, so it will be conserved on the database and it will be updated on Google Calendar or in Notion.")

    else:
        print('There are no events saved')
