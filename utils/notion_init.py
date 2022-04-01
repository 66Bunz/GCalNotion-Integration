

def notion_init(credentials_db):
    """
    Initializes the Notion Service.
    Gets all the things that are needed to make API calls to the Notion API

    Returns:
        notion_database, notion_headers
    """

    notion_token = credentials_db.find_one({'name': 'notion_token'})['value']
    notion_database = credentials_db.find_one({'name': 'notion_database'})['value']

    notion_headers = {
        'Authorization': f'Bearer {notion_token}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-02-22'
    }
    print('Notion service initialized')
    return notion_database, notion_headers
