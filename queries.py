SELECT_ALL_CANDIDATE_STATES = """SELECT id, name, group_id, resolved FROM CandidateState;"""

SELECT_ALL_GROUP_STATES = """SELECT id, name FROM GroupState;"""

INSERT_OR_REPLACE_CANDIDATE_STATE_name = """INSERT OR REPLACE INTO CandidateState (name) VALUES (?);"""

INSERT_OR_REPLACE_GROUP_STATE_name = """INSERT OR REPLACE INTO GroupState (name) VALUES (?);"""

# for each candidate who is not resolved and is not held,
# set their group id to be that of their most preferred group that is claiming them
DO_ROUND = """UPDATE CandidateState as cs 
	SET group_id = (SELECT gc.id FROM CandidatePreferences as cp 
				INNER JOIN GroupClaims as gc 
				ON cp.id = gc.candidate_id AND cp.group_id = gc.id
				WHERE cp.id = cs.id 
				ORDER BY cp.priority ASC
				LIMIT 1), 
	resolved = 1
	WHERE resolved = 0 AND 
	NOT EXISTS (SELECT 1 FROM GroupHolds as gh WHERE gh.candidate_id = cs.id LIMIT 1);"""

