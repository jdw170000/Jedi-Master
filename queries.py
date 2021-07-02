CREATE_GROUP_STATE = """CREATE TABLE IF NOT EXISTS GroupState (
			id INTEGER PRIMARY KEY, 
			name TEXT UNIQUE NOT NULL
			);"""

CREATE_CANDIDATE_STATE = """CREATE TABLE IF NOT EXISTS CandidateState (
			id INTEGER PRIMARY KEY,
			name TEXT UNIQUE NOT NULL, 
			group_id INTEGER NULL,
			resolved INTEGER DEFAULT 0,
			CONSTRAINT fk_groups
				FOREIGN KEY (group_id)
				REFERENCES GroupState(id)
				ON DELETE SET NULL
			);"""

CREATE_CANDIDATE_PREFERENCES = """CREATE TABLE IF NOT EXISTS CandidatePreferences (
				id INTEGER NOT NULL,
				group_id INTEGER NOT NULL,
				priority INTEGER NOT NULL,
				PRIMARY KEY (id, group_id, priority),
				CONSTRAINT fk_candidates
					FOREIGN KEY (id)
					REFERENCES CandidateState(id)
					ON DELETE CASCADE,
				CONSTRAINT fk_groups
					FOREIGN KEY (group_id)
					REFERENCES GroupState(id)
					ON DELETE CASCADE
				);"""

CREATE_GROUP_CLAIMS = """CREATE TABLE IF NOT EXISTS GroupClaims (
			id INTEGER NOT NULL,
			candidate_id INTEGER NOT NULL,
			PRIMARY KEY (id, candidate_id),
			CONSTRAINT fk_candidates
				FOREIGN KEY (candidate_id)
				REFERENCES CandidateState(id)
				ON DELETE CASCADE,
			CONSTRAINT fk_groups
				FOREIGN KEY (id)
				REFERENCES GroupState(id)
				ON DELETE CASCADE
			);"""

CREATE_GROUP_HOLDS = """CREATE TABLE IF NOT EXISTS GroupHolds (
			id INTEGER NOT NULL,
			candidate_id INTEGER NOT NULL,
			PRIMARY KEY (id, candidate_id),
			CONSTRAINT fk_candidates
				FOREIGN KEY (candidate_id)
				REFERENCES CandidateState(id)
				ON DELETE CASCADE,
			CONSTRAINT fk_groups
				FOREIGN KEY (id)
				REFERENCES GroupState(id)
				ON DELETE CASCADE
			);"""

INSERT_CANDIDATE_STATE_TEST_DATA = """INSERT OR IGNORE INTO CandidateState (name) VALUES ('john hammond'), ('alfred melbrook'), ('maria de''antonio');"""

INSERT_GROUP_STATE_TEST_DATA = """INSERT OR IGNORE INTO GroupState (name) VALUES ('songbirds'), ('plus ult cappella');"""

INSERT_CANDIDATE_PREFERENCES_TEST_DATA = """INSERT OR IGNORE INTO CandidatePreferences (id, group_id, priority) VALUES
					(1, 1, 1), (1, 2, 2),
					(2, 1, 2), (2, 2, 1),
					(3, 1, 1);"""

INSERT_GROUP_CLAIMS_TEST_DATA = """INSERT OR IGNORE INTO GroupClaims (id, candidate_id) VALUES
				(1, 1), (1, 3),
				(2, 1), (2, 2);"""

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
