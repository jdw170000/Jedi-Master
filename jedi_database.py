import sqlite3
import yaml
import random

from queries import *
from table_creation_queries import *
from test_data_queries import *

class JediDatabase:
	def __init__(self):
		config = None
		with open('db_config.yaml', 'r') as config_stream:
			config = yaml.safe_load(config_stream)

		self.connection = sqlite3.connect(config['db_name'])
		self.cur = self.connection.cursor()

	def __enter__(self):
		return self
	
	def __exit__(self, exception_type, exception_value, exception_traceback):
		self.cur.close()
		self.connection.close()

	def create_tables(self):
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

	def get_all_candidates(self):
		self.cur.execute(SELECT_ALL_CANDIDATE_STATES)
		return self.cur.fetchall()
	
	def get_all_groups(self):
		self.cur.execute(SELECT_ALL_GROUP_STATES)
		return self.cur.fetchall()

	def get_group_name(self, group_id):
		self.cur.execute("""SELECT name FROM GroupState WHERE id = ?;""", group_id)
		return self.cur.fetchone()
	
	def get_group_claims(self, group_id):
		self.cur.execute("""SELECT candidate_id FROM GroupClaims WHERE id = ?;""", group_id)
		return self.cur.fetchall()

	def get_group_holds(self, group_id):
		self.cur.execute("""SELECT candidate_id FROM GroupHolds WHERE id = ?;""", group_id)
		return self.cur.fetchall()

	def update_group_claims(self, group_id, claim_list):
		self.cur.execute("""DELETE FROM GroupClaims WHERE id = ?;""", group_id)
		for candidate_id in claim_list:
			self.cur.execute("""INSERT OR IGNORE INTO GroupClaims (id, candidate_id) VALUES (?, ?);""", group_id, candidate_id)
		self.connection.commit()
	
	def update_group_holds(self, group_id, hold_list):
		self.cur.execute("""DELETE FROM GroupHolds WHERE id = ?;""", group_id)
		for candidate_id in claim_list:
			self.cur.execute("""INSERT OR IGNORE INTO GroupHolds (id, candidate_id) VALUES (?, ?);""", group_id, candidate_id)
		self.connection.commit()

	def update_candidate_preferences(self, candidate_id, preference_list):
		self.cur.execute("""DELETE FROM CandidatePreferences WHERE id = ?;""", candidate_id)
		for priority, group_id in enumerate(preference_list):
			self.cur.execute("""INSERT OR IGNORE INTO CandidatePreferences (id, group_id, priority) VALUES (?, ?, ?);""", candidate_id, group_id, priority)
		self.connection.commit()

	def do_round(self):
		self.cur.execute(DO_ROUND)
		self.connection.commit()
