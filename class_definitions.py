from dataclasses import dataclass, asdict
from typing import List

import json

@dataclass(frozen = True)
class Identity:
	id: int
	name: str

@dataclass(frozen = True)
class Group(Identity):
	ready: bool = False

@dataclass(frozen = True)
class Candidate(Identity):
	group_id: int

# a Stake is a claim or a hold
@dataclass(frozen = True)
class Stake:
	group_id: int
	candidate_id: int

@dataclass(frozen = True)
class ModeratorView:
	candidates: List[Candidate] = None
	groups: List[Group] = None

	def serialize(self) -> str:
		candidates_serialized = json.dumps([asdict(candidate) for candidate in self.candidates])
		groups_serialized = json.dumps([asdict(group) for group in self.groups])
		return f'{{"candidates":{candidates_serialized}, "groups":{groups_serialized}}}' 

@dataclass(frozen = True)
class GroupView:
	name: str
	ready: bool
	available_candidates: List[Identity]
	unavailable_candidates: List[Identity]
	committed_candidates: List[Identity]
	claims: List[Stake]
	holds: List[Stake]	
	
	def serialize(self) -> str:
		available_candidates_serialized = json.dumps([asdict(candidate) for candidate in self.available_candidates])
		unavailable_candidates_serialized = json.dumps([asdict(candidate) for candidate in self.unavailable_candidates])
		committed_candidates_serialized = json.dumps([asdict(candidate) for candidate in self.committed_candidates])
		claims_serialized = json.dumps([asdict(claim) for claim in self.claims])
		holds_serialized = json.dumps([asdict(hold) for hold in self.holds])
		return f'{{"name":"{self.name}", "ready":{self.ready}, "available_candidates":{available_candidates_serialized}, "unavailable_candidates":{unavailable_candidates_serialized}, "committed_candidates":{committed_candidates_serialized}, "claims":{claims_serialized}, "holds":{holds_serialized}}}'
