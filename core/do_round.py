# look in class_definitions.py for the definitions of Candidate and Group

def do_round(candidate_dict, group_dict):

	claim_set_dict = {candidate_name: set() for candidate_name in candidate_dict.keys()}
	hold_set = set()
	
	# initialize the claim and hold sets for this round using the groups' input
	for group_name, group in group_dict:
		for candidate_name in group.claim_set:
			claim_set_dict[candidate_name].add(group_name)

		for candidate_name in group.hold_set:
			hold_set.add(candidate_name)

	# resolve candidates who have no holds
	candidates_to_resolve = claim_set_dict.keys() - hold_set

	for candidate_name in candidates_to_resolve:
		candidate = candidate_dict[candidate_name]
		claim_set = claim_set_dict[candidate_name]
		joined_group = candidate.resolve(claim_set)

		# update the groups' success, fail, and claim sets with the result of the resolution
		for group_name in claim_set:
			group = group_dict[group_name]
			group.claim_set.remove(candidate.name)
			if joined_group == group.name:
				group.success_set.add(candidate.name)
			else:
				group.fail_set.add(candidate.name)
	# the round is over; the candidate dictionary and group dictionary have been updated with the results	
