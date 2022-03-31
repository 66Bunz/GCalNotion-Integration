
import requests


def notion_patch(updated_event, notion_headers, notion_database, notionId):
    """
    Patches events on Notion.

    Args:
        updated_event:
        notion_headers:
        notion_database:
        notionId:
    """

    print('NOTION PATCH')

    notion_patch_url = f"https://api.notion.com/v1/pages/{notionId}"

    event_patch = {
        "parent": {"database_id": f"{notion_database}"},
        "properties": {
            "Nome": {
                "title": [
                    {
                        "text": {
                            "content": updated_event['title']
                        }
                    }
                ]
            },
            "Data": {
                "date": {
                    "start": updated_event['start'],
                    "end": updated_event['end']
                }
            },
        }
    }

    requests.request("PATCH", notion_patch_url, json=event_patch, headers=notion_headers)
    print(f'Evento aggiornato su Notion')
