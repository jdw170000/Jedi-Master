# for each candidate who is not resolved and is not held,
# set their group id to be that of their most preferred group that is claiming them
RESOLVE_CANDIDATES = """UPDATE CandidateState as cs 
	SET group_id = IFNULL((SELECT gc.id FROM CandidatePreferences as cp 
				INNER JOIN GroupClaims as gc 
				ON cp.id = gc.candidate_id AND cp.group_id = gc.id
				WHERE cp.id = cs.id 
				ORDER BY cp.priority ASC
				LIMIT 1), -1)
	WHERE group_id = 0 AND 
	NOT EXISTS (SELECT 1 FROM GroupHolds as gh WHERE gh.candidate_id = cs.id LIMIT 1);"""

