import pymongo
from pymongo import MongoClient
import os


def db_init():
	"""
	Initializes the MongoDB database.

	Returns:
		events_db, settings_db
	"""

	# TODO: Mettere link in variabile ambientale
	cluster = MongoClient(os.environ['mongodb_link'])
	db_cluster = cluster['TestDB']
	events_db = db_cluster['union']
	settings_db = db_cluster['settings']
	return events_db, settings_db

