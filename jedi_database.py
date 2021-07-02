import sqlite3
import yaml
import random

from queries import *

class JediDatabase:
	def __init__(self):
		config = None
		with open('db_config.yaml', 'r') as config_stream:
			config = yaml.load(config_stream)

		self.connection = sqlite3.connect(config['db_name'])
		self.cur = self.connection.cursor()

	def __enter__(self):
		return self
	
	def __exit__(self, exception_type, exception_value, exception_traceback):
		self.cur.close()
		self.connection.close()

	def create_database(self):
		print('creating group state...')
		self.cur.execute(CREATE_GROUP_STATE)
		print('creating candidate state...')
		self.cur.execute(CREATE_CANDIDATE_STATE)
		print('creating candidate preferences...')
		self.cur.execute(CREATE_CANDIDATE_PREFERENCES)
		print('creating group claims...')
		self.cur.execute(CREATE_GROUP_CLAIMS)
		print('creating group holds...')
		self.cur.execute(CREATE_GROUP_HOLDS)
		self.connection.commit()
		print('committed table creation.')

	def insert_test_data(self):
		self.cur.execute(INSERT_CANDIDATE_STATE_TEST_DATA)
		self.cur.execute(INSERT_GROUP_STATE_TEST_DATA)
		self.cur.execute(INSERT_CANDIDATE_PREFERENCES_TEST_DATA)
		self.cur.execute(INSERT_GROUP_CLAIMS_TEST_DATA)
		self.connection.commit()

	def do_round(self):
		self.cur.execute(DO_ROUND)
		self.connection.commit()

	def fetch(self):
		self.cur.execute('SELECT * FROM CandidateState;')
		return self.cur.fetchall()
