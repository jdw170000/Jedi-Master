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

	def get_group(self, group_id):
		self.cur.execute("""SELECT name, ready FROM GroupState WHERE id = ?;""", (group_id,))
		return self.cur.fetchone()
	
	def get_group_claims(self, group_id):
		self.cur.execute(SELECT_GROUP_CLAIMS_VIEW, (group_id,))
		return self.cur.fetchall()

	def get_group_holds(self, group_id):
		self.cur.execute(SELECT_GROUP_HOLDS_VIEW, (group_id,))
		return self.cur.fetchall()

	def get_group_view(self, group_id):
		group_name, ready = self.get_group(group_id)

		if group_name is None:
			return None

		candidate_states = self.get_all_candidates()
		
		committed = filter(lambda candidate: candidate[3] and candidate[2] == group_id, candidate_states)
		committed = set(map(lambda candidate: (candidate[0], candidate[1]), committed))
		
		unavailable = filter(lambda candidate: candidate[3] and candidate[2] != group_id, candidate_states)
		unavailable = set(map(lambda candidate: (candidate[0], candidate[1]), unavailable))
		
		claims = set(self.get_group_claims(group_id))
		holds = set(self.get_group_holds(group_id))

		# remove conflicts between claims, holds, and committed
		claims = claims - committed
		holds = holds - committed - claims

		available = filter(lambda candidate: not candidate[3], candidate_states)
		available = set(map(lambda candidate: (candidate[0], candidate[1]), available))

		# remove conflict between available and claims/holds
		available = available - claims - holds

		group_view = {
			'name': group_name, 
			'ready': ready,
			'claims': list(claims), 
			'holds': list(holds), 
			'committed': list(committed),
			'unavailable': list(unavailable),
			'available': list(available)
		}

		return group_view

	
	def clean_claims_and_holds(self):
		self.cur.execute("""DELETE FROM GroupClaims WHERE candidate_id IN (SELECT id FROM CandidateState WHERE resolved = 1);""")
		self.cur.execute("""DELETE FROM GroupHolds WHERE candidate_id IN (SELECT id FROM CandidateState WHERE resolved = 1);""")
		self.cur.execute("""DELETE FROM GroupHolds AS gh WHERE EXISTS(SELECT 1 FROM GroupClaims AS gc WHERE gc.id = gh.id AND gc.candidate_id = gh.candidate_id);""")
		self.connection.commit()

	def update_group_claims(self, group_id, claim_list):
		self.cur.execute("""DELETE FROM GroupClaims WHERE id = ?;""", (group_id,))
		for candidate_id in claim_list:
			self.cur.execute("""INSERT OR IGNORE INTO GroupClaims (id, candidate_id) VALUES (?, ?);""", (group_id, candidate_id))
		self.connection.commit()
	
	def update_group_holds(self, group_id, hold_list):
		self.cur.execute("""DELETE FROM GroupHolds WHERE id = ?;""", (group_id,))
		for candidate_id in hold_list:
			self.cur.execute("""INSERT OR IGNORE INTO GroupHolds (id, candidate_id) VALUES (?, ?);""", (group_id, candidate_id))
		self.connection.commit()

	def ready_group(self, group_id):
		self.cur.execute("""UPDATE GroupState SET ready = 1 WHERE id = ?;""", (group_id,))
		self.connection.commit()

	def update_candidate_preferences(self, candidate_id, preference_list):
		self.cur.execute("""DELETE FROM CandidatePreferences WHERE id = ?;""", (candidate_id,))
		for priority, group_id in enumerate(preference_list):
			self.cur.execute("""INSERT OR IGNORE INTO CandidatePreferences (id, group_id, priority) VALUES (?, ?, ?);""", (candidate_id, group_id, priority))
		self.connection.commit()

	def do_round(self):
		self.cur.execute(RESOLVE_CANDIDATES)
		self.cur.execute(CLEAR_RESOLVED_CLAIMS)
		self.cur.execute(CLEAR_RESOLVED_HOLDS)
		self.cur.execute(UNREADY_GROUPS)
		self.connection.commit()
