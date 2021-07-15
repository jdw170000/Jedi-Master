SELECT_ALL_CANDIDATE_STATES = """SELECT id, name, group_id, resolved FROM CandidateState;"""

SELECT_ALL_GROUP_STATES = """SELECT id, name, ready FROM GroupState;"""

INSERT_OR_REPLACE_CANDIDATE_STATE_name = """INSERT OR REPLACE INTO CandidateState (name) VALUES (?);"""

INSERT_OR_REPLACE_GROUP_STATE_name = """INSERT OR REPLACE INTO GroupState (name) VALUES (?);"""


SELECT_GROUP_CLAIMS_VIEW = """SELECT gc.candidate_id, cs.name 
			FROM GroupClaims as gc
			INNER JOIN CandidateState as cs
				ON gc.candidate_id = cs.id
			WHERE gc.id = ?;"""

SELECT_GROUP_HOLDS_VIEW = """SELECT gh.candidate_id, cs.name 
			FROM GroupHolds as gh
			INNER JOIN CandidateState as cs
				ON gh.candidate_id = cs.id
			WHERE gh.id = ?;"""

# for each candidate who is not resolved and is not held,
# set their group id to be that of their most preferred group that is claiming them
RESOLVE_CANDIDATES = """UPDATE CandidateState as cs 
	SET group_id = (SELECT gc.id FROM CandidatePreferences as cp 
				INNER JOIN GroupClaims as gc 
				ON cp.id = gc.candidate_id AND cp.group_id = gc.id
				WHERE cp.id = cs.id 
				ORDER BY cp.priority ASC
				LIMIT 1), 
	resolved = 1
	WHERE resolved = 0 AND 
	NOT EXISTS (SELECT 1 FROM GroupHolds as gh WHERE gh.candidate_id = cs.id LIMIT 1);"""


CLEAR_RESOLVED_CLAIMS = """DELETE FROM GroupClaims 
	WHERE candidate_id IN (SELECT id FROM CandidateState WHERE resolved = 1);"""

CLEAR_RESOLVED_HOLDS = """DELETE FROM GroupHolds 
	WHERE candidate_id IN (SELECT id FROM CandidateState WHERE resolved = 1);"""

UNREADY_GROUPS = """UPDATE GroupState SET ready = 0;"""
