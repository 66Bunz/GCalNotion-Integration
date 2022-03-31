

def notion_init(settings_db):
    """
    Initializes the Notion Service.
    Gets all the things that are needed to make API calls to the Notion API

    Returns:
        notion_database, notion_headers
    """

    notion_token = settings_db.find_one({'name': 'notion_token'})['value']
    notion_database = settings_db.find_one({'name': 'notion_database'})['value']

    notion_headers = {
        'Authorization': f'Bearer {notion_token}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-02-22'
    }

    return notion_database, notion_headers
