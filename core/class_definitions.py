class Candidate:
	def __init__(self):
		self.preference_list = []
		self.name = None
		self.resolved = False
		self.joined_group = None

	def resolve(self, claim_set):
		self.resolved = True
		#look at my preference list in order
		#greedily select the most preferred group who wants me
		for group_name in self.preference_list:
			if group_name in claim_set:
				self.joined_group = group_name
				return group_name
		#no group on my preference list wants me, return None
		return None

class Group:
	def __init__(self):
		self.name = None
		self.claim_set = set()
		self.hold_set = set()
		self.success_set = set()
		self.fail_set = set()
