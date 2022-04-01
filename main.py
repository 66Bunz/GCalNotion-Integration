
import schedule
import os
import sys

from utils import keep_alive, db_init, gcal_init, notion_init, db_load


def authenticate():
	print("To use this app you need to authenticate yourself")
	print("Insert the password below:")
	pwd = input()
	print(pwd)
	print(os.environ['repl_pwd'])
	if pwd == os.environ['repl_pwd']:
		print('Correct password... Loading Flask Server and starting the main funtion...')
		keep_alive()
		main()
	else:
		print('Incorrect password... This service will now exit.')
		sys.exit()


def main():
    """
    Main function that runs every initialization and periodically runs calendars and database updates.
    """
	
    print('Starting database service')
    events_db, credentials_db = db_init()
    print('Starting Google Calendar service')
    gcal_service, gcal_calendarid = gcal_init(credentials_db)
    print('Starting Notion service')
    notion_database, notion_headers = notion_init(credentials_db)

    # list_10(gcal_service, collection)
    # one_week(gcal_service, collection)
    # three_weeks(gcal_service, collection)

    db_load(gcal_service, gcal_calendarid, notion_headers, notion_database, events_db)

    # schedule.every(1).minutes.do(one_week)
    # schedule.every(5).minutes.do(three_weeks)
    # schedule.every(20).minutes.do(eight_weeks)
    # schedule.every(10).minutes.do()
    # schedule.every(10).minutes.do()


if __name__ == '__main__':
    authenticate()
