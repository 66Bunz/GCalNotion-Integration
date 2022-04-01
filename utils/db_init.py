
import pymongo
from pymongo import MongoClient
import os


def db_init():
	"""
	Initializes the MongoDB database.

	Returns:
		events_db, credentials_db
	"""

	# TODO: Mettere link in variabile ambientale
	cluster = MongoClient(os.environ['mongodb_link'])
	db_cluster = cluster[os.environ['db_cluster']]
	events_db = db_cluster[os.environ['event_db']]
	credentials_db = db_cluster[os.environ['credentials_db']]
	return events_db, credentials_db

