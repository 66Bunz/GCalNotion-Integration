
import requests
import datetime
import sys
import json


def notion_load(event, notion_headers, notion_database, events_db, limits):
    """
    Loads events on Notion.

    Args:
        event:
        notion_headers:
        notion_database:
        events_db:
        limits:
    """

    notion_post_url = 'https://api.notion.com/v1/pages'

    # if event['location'] is None:
    #     event_post = {
    #         "parent": {"database_id": f"{notion_database}"},
    #         "properties": {
    #             "Nome": {
    #                 "title": [
    #                     {
    #                         "text": {
    #                             "content": event['title']
    #                         }
    #                     }
    #                 ]
    #             },
    #             "Data": {
    #                 "date": {
    #                     "start": event['start'],
    #                     "end": event['end']
    #                 }
    #             },
    #             # "Tag": {
    #             #     "select": [
    #             #         {
    #             #             "color": event['color']
    #             #         }
    #             #     ]
    #             # },
    #             # "Posizione": {
    #             #     "rich_text": [
    #             #         {
    #             #             "text": {
    #             #                 "content": event['location']
    #             #             }
    #             #         }
    #             #     ]
    #             # }
    #         }
    #     }

    event_post = {
        "parent": {"database_id": f"{notion_database}"},
        "properties": {
            "Nome": {
                "title": [
                    {
                        "text": {
                            "content": event['title']
                        }
                    }
                ]
            },
            "Data": {
                "date": {
                    "start": event['start'],
                    "end": event['end']
                }
            },
        }
    }

    just_posted_event = requests.post(notion_post_url, headers=notion_headers, json=event_post)
    just_posted_event = just_posted_event.json()
    # print(just_posted_event)
    print(f'Evento creato su Notion')

    # ---------------------------------------------------

    notion_read_url = f"https://api.notion.com/v1/databases/{notion_database}/query"

    now_utc = datetime.datetime.utcnow()

    if limits == 'OneMin':
        # print("OneMin")
        week_decrease = datetime.timedelta(weeks=1)
        minLimit = now_utc - week_decrease
        minLimit = minLimit.isoformat() + 'Z'

        week_add = datetime.timedelta(weeks=1)
        maxLimit = now_utc + week_add
        maxLimit = maxLimit.isoformat() + 'Z'

        filters = json.dumps(
            {
                "page_size": 100,
                "filter": {
                    "and": [
                        {
                            "property": "title",
                            "rich_text": {
                                "is_not_empty": True
                            }
                        },
                        {
                            "property": "Data",
                            "date": {
                                "after": minLimit
                            }
                        },
                        {
                            "property": "Data",
                            "date": {
                                "before": maxLimit
                            }
                        }
                    ]
                }
            }
        )

    elif limits == 'FiveMin':
        # print("FiveMin")
        week_decrease = datetime.timedelta(weeks=2)
        minLimit = now_utc - week_decrease
        minLimit = minLimit.isoformat() + 'Z'

        week_add = datetime.timedelta(weeks=3)
        maxLimit = now_utc + week_add
        maxLimit = maxLimit.isoformat() + 'Z'

        filters = json.dumps(
            {
                "page_size": 100,
                "filter": {
                    "and": [
                        {
                            "property": "title",
                            "rich_text": {
                                "is_not_empty": True
                            }
                        },
                        {
                            "property": "Data",
                            "date": {
                                "after": minLimit
                            }
                        },
                        {
                            "property": "Data",
                            "date": {
                                "before": maxLimit
                            }
                        }
                    ]
                }
            }
        )

    elif limits == 'TwentyMin':
        # print("TwentyMin")
        week_decrease = datetime.timedelta(weeks=4)
        minLimit = now_utc - week_decrease
        minLimit = minLimit.isoformat() + 'Z'

        week_add = datetime.timedelta(weeks=8)
        maxLimit = now_utc + week_add
        maxLimit = maxLimit.isoformat() + 'Z'

        filters = json.dumps(
            {
                "page_size": 100,
                "filter": {
                    "and": [
                        {
                            "property": "title",
                            "rich_text": {
                                "is_not_empty": True
                            }
                        },
                        {
                            "property": "Data",
                            "date": {
                                "after": minLimit
                            }
                        },
                        {
                            "property": "Data",
                            "date": {
                                "before": maxLimit
                            }
                        }
                    ]
                }
            }
        )

    else:
        print(f'Error, limits parameter gave an unexpected value: {limits}')
        sys.exit()

    try:
        events_result = requests.post(notion_read_url, data=filters, headers=notion_headers)
        events_result.raise_for_status()
        events = events_result.json()['results']
        # print(events)

        if not events:
            print('No events found.')

        for event in events:
            # print(event)
            notionID = event['id']
            notion_updated = event['last_edited_time']

            # print(event)
            if just_posted_event['properties']['Nome']['title'][0]['text']['content'] == event['properties']['Nome']['title'][0]['text']['content']:
                print('Aggiungendo notionID sul DB')
                # print(notionID)
                notion_event = {
                    "notionID": notionID,
                    "notion_updated": notion_updated
                }
                events_db.update_one(
                    {'title': just_posted_event['properties']['Nome']['title'][0]['text']['content']},
                    {'$set': notion_event}
                )
                print('NotionID aggiunto sul DB')

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as error:
        print(f'An error occurred: {error}')
