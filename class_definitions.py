from typing import List, TypedDict

class Candidate(TypedDict, total=False):
	id: int
	name: str
	group_id: int

class Group(TypedDict, total=False):
	id: int
	name: str
	ready: bool

class Stake(TypedDict, total=False):
	candidate_id: int
	group_id: int 

class ModeratorView(TypedDict, total=False):
	candidates: List[Candidate]
	groups: List[Group]

class GroupView(TypedDict, total=False):
	name: str
	ready: bool
	available_candidates: List[Candidate]
	unavailable_candidates: List[Candidate]
	committed_candidats: List[Candidate]
	claims: List[Stake]
	holds: List[Stake] 
