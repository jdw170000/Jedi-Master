import sqlite3
from csv import reader as csv_reader

from itertools import zip_longest

from queries import *
from table_creation_queries import *

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

        def create_tables(self):
                self.cur.execute(CREATE_GROUP_STATE)
                self.cur.execute(CREATE_CANDIDATE_STATE)
                self.cur.execute(CREATE_CANDIDATE_PREFERENCES)
                self.cur.execute(CREATE_GROUP_CLAIMS)
                self.cur.execute(CREATE_GROUP_HOLDS)
                self.connection.commit()

        def initialize_from_google_form_response_csv(self, response_file):
                # load into a csv reader and skip header
                reader = csv_reader([line.decode() for line in response_file.readlines()])
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
        
        def decode_group(self, resolved, group_id):
                if resolved:
                        if group_id:
                                return group_id
                        else:
                                return -1
                else:
                        return 0
        def encode_group(self, encoded_id):
                if encoded_id > 0:
                        return (1, encoded_id)
                if encoded_id == 0:
                        return (0, None)
                return (1, None)

        def get_moderator_total_view(self):
                candidate_states = self.get_all_candidates();

                candidates = map(lambda candidate: (candidate[0], candidate[1], self.decode_group(candidate[3], candidate[2])), candidate_states)

                groups = self.get_all_groups();
                
                moderator_view = {
                        'candidates': list(candidates),
                        'groups': list(groups)
                }
                
                return moderator_view
        
        def get_moderator_candidates(self):
                candidate_states = self.get_all_candidates()
                candidates = map(lambda candidate: (candidate[0], self.decode_group(candidate[3], candidate[2])), candidate_states)
                return { 'candidates': list(candidates) }
        
        def get_moderator_groups(self):
                self.cur.execute("""SELECT id, ready FROM GroupState;""")
                return { 'groups': self.cur.fetchall() }
                
        def get_moderator_view(self):
                moderator_view = self.get_moderator_candidates()
                moderator_view.update(self.get_moderator_groups())
                return moderator_view;

        def post_moderator_candidates(self, candidates):
                for candidate in candidates:
                        resolved, group_id = self.encode_group(candidate[1])
                        self.cur.execute("""UPDATE CandidateState SET resolved = ?, group_id = ? WHERE id = ?;""", (resolved, group_id, candidate[0]))
                self.connection.commit()

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
        
        def generate_moderator_results(self):
                self.cur.execute("""SELECT id, name from GroupState;""")
                groups = self.cur.fetchall()

                groups.insert(0, (-1, 'No Group'))

                assignments = dict()
                for group in groups:
                        resolved, group_id = self.encode_group(group[0])
                        self.cur.execute("""SELECT name from CandidateState WHERE resolved = ? AND group_id IS ?;""", (resolved, group_id))
                        assignments[group[0]] = self.cur.fetchall()

                results = ",".join([group[1].upper() for group in groups])
                results += '\n'         

                assignment_data = zip_longest(*assignments.values())
        
                for row in assignment_data:
                        for name in row:
                                results += ',' if name is None else f'{name[0]},'
                        results += '\n'

                return results  

        def generate_results(self, client_id):
                self.cur.execute("""SELECT name from GroupState WHERE id = ?;""", (client_id, ))
                name = self.cur.fetchone()[0].upper()
                results = f'{name}\n'

                self.cur.execute("""SELECT name FROM CandidateState WHERE resolved=1 AND group_id = ?;""", (client_id, ))
                for candidate_name in self.cur:
                        results += f'{candidate_name[0]}\n'

                return results
