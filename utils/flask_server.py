
import os
import flask
import requests
import json

from threading import Thread

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError




app = flask.Flask('GCalNotion-Integration')
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = os.environ['flask_token']


@app.route('/')
def index():
	return "I'm alive"



def keep_alive():  
    t = Thread(target=start_server)
    t.start()


def start_server():
	"""
    Initializes the Flask Server.
    """
	
	# This OAuth 2.0 access scope allows for full read/write access to the
	# authenticated user's account and requires requests to use an SSL connection.
	
	# When running locally, disable OAuthlib's HTTPs verification.
	# ACTION ITEM for developers:
	# 	When running in production *do not* leave this option enabled.
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'
	
	# Specify a hostname and port that are set as a valid redirect URI
	# for your API project in the Google API Console.
	app.run('0.0.0.0', 8080, debug=True)


@app.route('/authorize')
def gcal_auth(credentials_db, SCOPES):
	credentials = credentials_db.find_one({'name': 'gcal_credentials'})['value']

	
	# Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
	flow = Flow.from_client_config(credentials, SCOPES)

	flow.redirect_uri = flask.url_for('oauth2callback', _external=True, _scheme='https')

	authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
	
	# Store the state so the callback can verify the auth server response.
	flask.session['state'] = state

	
	
	return flask.redirect(authorization_url)
	



@app.route('/oauth2callback')
def oauth2callback(gcal_token, SCOPES):
	# Specify the state when creating the flow in the callback so that it can
	# verified in the authorization server response.
	state = flask.session['state']
	
	flow = Flow.from_authorized_user_info(gcal_token, SCOPES, state=state)
	flow.redirect_uri = flask.url_for('oauth2callback', _external=True, _scheme='https')
	
	# Use the authorization server's response to fetch the OAuth 2.0 tokens.
	authorization_response = flask.request.url
	flow.fetch_token(authorization_response=authorization_response)
	
	# Store credentials in the session.
	# ACTION ITEM: In a production app, you likely want to save these
	#              credentials in a persistent database instead.
	creds = flow.credentials

	
	flask.session['credentials'] = credentials_to_dict(creds)
	
	return creds


def credentials_to_dict(creds):
	return {'token': creds.token,
          'refresh_token': creds.refresh_token,
          'token_uri': creds.token_uri,
          'client_id': creds.client_id,
          'client_secret': creds.client_secret,
          'scopes': creds.scopes}














@app.route('/build')
def gcal_build(creds, gcal_calendarid):
	
	# if 'credentials' not in flask.session:
		# return flask.redirect('authorize')
	
	# Load credentials from the session.
	# credentials = Credentials(**flask.session['credentials'])

	try:
        # Tries to build the Google Calendar Service
		gcal_service = build('calendar', 'v3', credentials=creds)
		return gcal_service, gcal_calendarid

	except HttpError as error:
		print(f'An error occurred: {error}')
	
	# Save credentials back to session in case access token was refreshed.
	# ACTION ITEM: In a production app, you likely want to save these
	# credentials in a persistent database instead.
	# flask.session['credentials'] = credentials_to_dict(credentials)
	
	# return flask.jsonify(**files)




def print_index_table():
	return ('<table>' +
          '<tr><td><a href="/build">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/build">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


@app.route('/revoke')
def revoke():
	if 'credentials' not in flask.session:
		return ('You need to <a href="/authorize">authorize</a> before ' +
			'testing the code to revoke credentials.')
	
	credentials = Credentials(flask.session['credentials'])
	
	revoke = requests.post('https://oauth2.googleapis.com/revoke',
		params={'token': credentials.token},
		headers = {'content-type': 'application/x-www-form-urlencoded'})
	
	status_code = getattr(revoke, 'status_code')
	if status_code == 200:
		return('Credentials successfully revoked.' + print_index_table())
	else:
		return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
	if 'credentials' in flask.session:
		del flask.session['credentials']
	return ('Credentials have been cleared.<br><br>' +
          print_index_table())

