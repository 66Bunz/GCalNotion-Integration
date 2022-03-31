
import schedule

from utils import db_init, gcal_init, notion_init, db_load
from keep_alive import keep_alive


def main():
    """
    Main function that runs every initialization and periodically runs calendars and database updates.
    """

    events_db, settings_db = db_init()
    gcal_service, gcal_calendarid = gcal_init(settings_db)
    notion_database, notion_headers = notion_init(settings_db)

    # list_10(gcal_service, collection)
    # one_week(gcal_service, collection)
    # three_weeks(gcal_service, collection)

    db_load(gcal_service, gcal_calendarid, notion_headers, notion_database,
            events_db)

    # schedule.every(1).minutes.do(one_week)
    # schedule.every(5).minutes.do(three_weeks)
    # schedule.every(20).minutes.do(eight_weeks)
    # schedule.every(10).minutes.do()
    # schedule.every(10).minutes.do()


if __name__ == '__main__':
    keep_alive()
    main()
