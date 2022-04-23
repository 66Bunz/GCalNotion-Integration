
import schedule
import os
import sys
import time

from utils import keep_alive, db_init, gcal_init, notion_init, db_load, db_delete


def authenticate():
    """
    Authentication function.
    """

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

    # db_delete(gcal_service, gcal_calendarid, notion_headers, notion_database, events_db)

    # db_load(gcal_service, gcal_calendarid, notion_headers, notion_database, events_db, limits="TwentyMin")

    print('Running Job...')

    schedule.every(1).minutes.do(
        job, gcal_service=gcal_service, gcal_calendarid=gcal_calendarid, notion_headers=notion_headers, notion_database=notion_database, events_db=events_db, limits="OneMin"
        )

    schedule.every(5).minutes.do(
        job, gcal_service=gcal_service, gcal_calendarid=gcal_calendarid, notion_headers=notion_headers, notion_database=notion_database, events_db=events_db, limits="FiveMin"
        )

    schedule.every(20).minutes.do(
        job, gcal_service=gcal_service, gcal_calendarid=gcal_calendarid, notion_headers=notion_headers, notion_database=notion_database, events_db=events_db, limits="TwentyMin"
        )

    while True:
        schedule.run_pending()
        time.sleep(1)


def job(gcal_service, gcal_calendarid, notion_headers, notion_database, events_db, limits):
    db_delete(gcal_service, gcal_calendarid, notion_headers, notion_database)
    db_load(gcal_service, gcal_calendarid, notion_headers, notion_database, events_db, limits)


if __name__ == '__main__':
    authenticate()
    main()
