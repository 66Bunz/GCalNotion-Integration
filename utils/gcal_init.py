
import json
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


def gcal_init(credentials_db):
	"""
	Initializes the Google Calendar Service.

	Args:
		credentials_db: MongoDB settings database

	Returns:
		gcal_service, gcal_calendarid

	Raises:
		HttpError
	"""

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	gcal_calendarid = credentials_db.find_one({'name': 'gcal_calendarid'})['value']

	creds = None
	
	if credentials_db.find_one({'name': 'gcal_token'}):
		gcal_token = credentials_db.find_one({'name': 'gcal_token'})['value']
		creds = Credentials.from_authorized_user_info(gcal_token, SCOPES)
		try:
			# Tries to build the Google Calendar Service
			gcal_service = build('calendar', 'v3', credentials=creds)
			print('Google Calendar service initialized')
			return gcal_service, gcal_calendarid
	
		except HttpError as error:
			print(f'An error occurred: {error}')

	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
			# Save the credentials for the next run
			gcal_token_post = {
				'name': 'gcal_token',
				'value': json.loads(creds.to_json())
			}
			credentials_db.insert_one(gcal_token_post)
			try:
				# Tries to build the Google Calendar Service
				gcal_service = build('calendar', 'v3', credentials=creds)
				print('Google Calendar service initialized')
				return gcal_service, gcal_calendarid
		
			except HttpError as error:
				print(f'An error occurred: {error}')

		else:
			print('The credentials weren\'t saved on the database, so you need to run the <Create_Credentials> app!')
			sys.exit()
