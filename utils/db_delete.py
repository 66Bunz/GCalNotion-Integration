
import requests

def db_delete(gcal_service, gcal_calendarid, notion_headers, notion_database, events_db):
    """
    Deletes events on the database and from the calendars.

    Args:
       gcal_service:
       gcal_calendarid:
       notion_headers:
       notion_database:
       events_db:
    """


    for event in events_db.find():
        gcal_id = event['gcalID']
        notion_id = event['notionID']
        # notion_id = uuid.UUID(notion_id).hex
        check_notion = True

        read_url = f"https://api.notion.com/v1/pages/{notion_id}"

        gcal_event = gcal_service.events().get(calendarId=gcal_calendarid, eventId=event['gcalID']).execute()

        if gcal_event['status'] == 'cancelled':
            event_patch = {
                "archived": True
            }
            requests.request("PATCH", read_url, json=event_patch, headers=notion_headers)
            events_db.delete_one({"gcalID":gcal_id})
            print(f"{event['title']} was deteled in GCal, so {event['title']} was deleted from Notion and database too.")
            check_notion = False
        elif gcal_event['status'] == 'confirmed':
            print("No event was deleted from GCal.")
        else:
            print(f'Error: {gcal_event}')

#-----------------------------------------------------------------------

        response = requests.request("GET", read_url, headers=notion_headers)

        if check_notion:
            if response.json()['archived'] == True:
                gcal_service.events().delete(calendarId=gcal_calendarid, eventId=gcal_id).execute()
                events_db.delete_one({"notionID":notion_id})
                print(f"{event['title']} was deteled in Notion, so {event['title']} was deleted from GCal and database too.")
            elif response.json()['archived'] == False:
                print("No event was deleted from Notion.")
            else:
                print(f'Error: {response.text}')
        else:
            print('Error')
