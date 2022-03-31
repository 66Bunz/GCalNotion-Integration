
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


def gcal_init(settings_db):
    """
    Initializes the Google Calendar Service.

    Args:
        settings_db: MongoDB settings database

    Returns:
        gcal_service, gcal_calendarid

    Raises:
        HttpError
    """

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    gcal_calendarid = settings_db.find_one({'name': 'gcal_calendarid'})['value']

    creds = None
    if settings_db.find_one({'name': 'gcal_token'}):
        gcal_token = settings_db.find_one({'name': 'gcal_token'})['value']
        creds = Credentials.from_authorized_user_info(gcal_token, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            credentials = settings_db.find_one({'name': 'gcal_credentials'})['value']
            flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        gcal_token_post = {
            'name': 'gcal_token',
            'value': json.loads(creds.to_json())
        }
        settings_db.insert_one(gcal_token_post)

    try:
        # Tries to build the Google Calendar Service
        gcal_service = build('calendar', 'v3', credentials=creds)
        return gcal_service, gcal_calendarid

    except HttpError as error:
        print(f'An error occurred: {error}')
