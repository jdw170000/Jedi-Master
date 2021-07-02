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
