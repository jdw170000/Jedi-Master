import sqlite3
import csv
import itertools
import more_itertools

from dataclasses import dataclass
from typing import List

from queries import RESOLVE_CANDIDATES
from table_creation_queries import *
from class_definitions import Identity, Group, Candidate, Stake, ModeratorView, GroupView

class InvalidGroupException(Exception):
	pass

class NotModeratorException(Exception):
	pass

class JediDatabase:
	def __init__(self):
		DB_NAME = 'my_jedi_db'
		self.connection = sqlite3.connect(DB_NAME)
		self.cur = self.connection.cursor()

	def __enter__(self):
		return self
	
	def __exit__(self, exception_type, exception_value, exception_traceback):
		self.cur.close()
		self.connection.close()

	def get_all_candidates(self) -> List[Candidate]:
		self.cur.execute("""SELECT id, name, group_id FROM CandidateState;""")
		return [Candidate(id = result[0], name = result[1], group_id = result[2]) for result in self.cur.fetchall()]
	
	def get_all_groups(self) -> List[Group]:
		self.cur.execute("""SELECT id, name, ready FROM GroupState;""")
		return [Group(id = result[0], name = result[1], ready = result[2]) for result in self.cur.fetchall()]
		
class InitializerDatabase(JediDatabase):
	def create_tables(self) -> None:
		self.cur.execute(CREATE_GROUP_STATE)
		self.cur.execute(CREATE_CANDIDATE_STATE)
		self.cur.execute(CREATE_CANDIDATE_PREFERENCES)
		self.cur.execute(CREATE_GROUP_CLAIMS)
		self.cur.execute(CREATE_GROUP_HOLDS)
		self.connection.commit()

class ModeratorDatabase(JediDatabase):
	def __init__(self, client_id: int):
		if client_id != -1:
			raise NotModeratorException()
		super().__init__()

	def get_view(self) -> ModeratorView:
		candidates = self.get_all_candidates();
		groups = self.get_all_groups();
		return ModeratorView(candidates = candidates, groups = groups)
	
	def post_candidates(self, candidates: List[Candidate]) -> None:
		for candidate in candidates:
			self.cur.execute("""UPDATE CandidateState SET group_id = ? WHERE id = ?;""", (candidate.group_id, candidate.id))
		self.connection.commit()

	def populate_from_google_form_response_csv(self, response_file) -> None:
		# load into a csv reader and skip header
		reader = csv.reader([line.decode() for line in response_file.readlines()])
		next(reader)
		for row in reader:
			# unpack relevant information from the row
			_, name, _, *preferences, _ = row
			# remove empty preferences
			preferences = [pref for pref in preferences if pref and pref != 'No Group']
			# create the candidate state
			self.cur.execute("""INSERT OR IGNORE INTO CandidateState (name) VALUES (?);""", (name, ))
			# ensure the preferred groups exist
			if preferences:
				self.cur.execute(f"""INSERT OR IGNORE INTO GroupState (name) VALUES {', '.join(['(?)']*len(preferences))};""", preferences)
			# create the candidate's preferences
			for priority, group in enumerate(preferences, 1):
				self.cur.execute("""INSERT OR IGNORE INTO CandidatePreferences (id, group_id, priority) SELECT c.id, g.id, ? FROM CandidateState AS c INNER JOIN GroupState AS g ON c.name=? and g.name=?;""", (priority, name, group))
		
		self.connection.commit()	       
	
	def do_round(self) -> None:
		self.cur.execute(RESOLVE_CANDIDATES)
		self.cur.execute("""UPDATE GroupState SET Ready = 0;""")
		self.connection.commit()

	def generate_moderator_results(self) -> str:
		groups = self.get_all_groups()

		no_group = Group(id = -1, name = 'No Group')
		groups.insert(0, no_group)

		assignments = dict()
		for group in groups:
			self.cur.execute("""SELECT name from CandidateState WHERE group_id = ?;""", (group.id))
			assignments[group.id] = [result[0] for result in self.cur.fetchall()]

		results = ",".join([group.name.upper() for group in groups])
		results += '\n'		

		assignment_data = itertools.zip_longest(*assignments.values())
	
		for row in assignment_data:
			for name in row:
				results += ',' if name is None else f'{name},'
			results += '\n'

		return results	

class GroupDatabase(JediDatabase):
	def __init__(self, group_id):
		self.group_id = group_id
		super().__init__()

	def get_group(self) -> Group:
		self.cur.execute("""SELECT name, ready FROM GroupState WHERE id = ?;""", (self.group_id,))
		
		result = self.cur.fetchone()
		if(result is None):
			raise InvalidGroupException(f'Selected group ({self.group_id}) does not exist') 

		return Group(id = self.group_id, name = result[0], ready = result[1])
	
	def get_claims(self) -> List[Stake]:
		self.cur.execute("""SELECT candidate_id FROM GroupClaims WHERE id = ?;""", (self.group_id,))
		return [Stake(group_id = self.group_id, candidate_id = result[0]) for result in self.cur.fetchall()]

	def get_holds(self) -> List[Stake]:
		self.cur.execute("""SELECT candidate_id FROM GroupHolds WHERE id = ?;""", (self.group_id,))
		return [Stake(group_id = self.group_id, candidate_id = result[0]) for result in self.cur.fetchall()]
	
	def clean_claims_and_holds(self) -> None:
		self.cur.execute("""DELETE FROM GroupClaims WHERE candidate_id IN (SELECT id FROM CandidateState AS cs WHERE cs.group_id <> 0);""")
		self.cur.execute("""DELETE FROM GroupHolds WHERE candidate_id IN (SELECT id FROM CandidateState AS cs WHERE cs.group_id <> 0);""")
		self.cur.execute("""DELETE FROM GroupHolds AS gh WHERE EXISTS(SELECT 1 FROM GroupClaims AS gc WHERE gc.id = gh.id AND gc.candidate_id = gh.candidate_id);""")
		self.connection.commit()

	def update_claims(self, claim_list: List[Stake]) -> None:
		self.cur.execute("""DELETE FROM GroupClaims WHERE id = ?;""", (self.group_id,))
		for claim in claim_list:
			self.cur.execute("""INSERT OR IGNORE INTO GroupClaims (id, candidate_id) VALUES (?, ?);""", (self.group_id, claim.candidate_id))
		self.connection.commit()
	
	def update_holds(self, hold_list: List[Stake]) -> None:
		self.cur.execute("""DELETE FROM GroupHolds WHERE id = ?;""", (self.group_id,))
		for hold in hold_list:
			self.cur.execute("""INSERT OR IGNORE INTO GroupHolds (id, candidate_id) VALUES (?, ?);""", (self.group_id, hold.candidate_id))
		self.connection.commit()

	def ready(self) -> None:
		self.cur.execute("""UPDATE GroupState SET ready = 1 WHERE id = ?;""", (self.group_id,))
		self.connection.commit()

	def get_view(self) -> GroupView:
		group = self.get_group()

		remaining_candidates = self.get_all_candidates()
	       
		# a candidate is committed to my group if they have my group id
		is_committed = lambda candidate: candidate.group_id == self.group_id
		remaining_candidates, committed = more_itertools.partition(is_committed, remaining_candidates)

		# a candidate is unavailable if they are not committed to me and they are assigned (group id != 0)
		is_unavailable = lambda candidate: candidate.group_id != 0
		remaining_candidates, unavailable = more_itertools.partition(is_unavailable, remaining_candidates)

		# a candidate is claimed by me if they are available and I am claiming them
		my_claims = self.get_claims()
		is_claimed = lambda candidate: Stake(group_id = self.group_id, candidate_id = candidate.id) in my_claims
		remaining_candidates, claims = more_itertools.partition(is_claimed, remaining_candidates)

		# a candidate is held by me if they are available, I am not claiming them, and I am holding them
		my_holds = self.get_holds()
		is_held = lambda candidate: Stake(group_id = self.group_id, candidate_id = candidate.id) in my_holds
		remaining_candidates, holds = more_itertools.partition(is_held, remaining_candidates)
		
		# a candidate is available if they are not assigned, claimed, or held
		available = remaining_candidates
		
		return GroupView(
			name = group.name, 
			ready = group.ready,
			claims = list(claims), 
			holds = list(holds), 
			committed_candidates = list(committed),
			unavailable_candidates = list(unavailable),
			available_candidates = list(available)
		)

	def generate_results(self):
		group = self.get_group()
		results = f'{group.name.upper()}\n'

		self.cur.execute("""SELECT name FROM CandidateState WHERE group_id = ?;""", (self.group_id, ))
		for candidate_name in self.cur:
			results += f'{candidate_name[0]}\n'

		return results

