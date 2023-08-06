from math import sqrt, pow

def AreYouErnesto(name):
	if(name == "Ernesto"):
		return True
	return False

class vecstuff():
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def normalvector(self):
		unit = sqrt(pow(self.x,2)+pow(self.y,2)+pow(self.z,2))
		return [self.x/unit, self.y/unit, self.z/unit]

	def length(self):
		return sqrt(pow(self.x,2)+pow(self.y,2)+pow(self.z,2))
			
