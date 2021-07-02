INSERT_CANDIDATE_STATE_TEST_DATA = """INSERT OR IGNORE INTO CandidateState (name) VALUES ('john hammond'), ('alfred melbrook'), ('maria de''antonio'), ('test noprefs');"""

INSERT_GROUP_STATE_TEST_DATA = """INSERT OR IGNORE INTO GroupState (name) VALUES ('songbirds'), ('plus ult cappella');"""

INSERT_CANDIDATE_PREFERENCES_TEST_DATA = """INSERT OR IGNORE INTO CandidatePreferences (id, group_id, priority) VALUES
					(1, 1, 1), (1, 2, 2),
					(2, 1, 2), (2, 2, 1),
					(3, 1, 1);"""

INSERT_GROUP_CLAIMS_TEST_DATA = """INSERT OR IGNORE INTO GroupClaims (id, candidate_id) VALUES
				(1, 1), (1, 3),
				(2, 1), (2, 2);"""

