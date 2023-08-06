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
		
def DoF2t_test(s1, s2, n1, n2):
	num = pow( pow(s1,2)/n1 + pow(s2,2)/n2 ,2)
	denom1 = pow(pow(s1,2)/n1,2)/(n1-1)
	denom2 = pow(pow(s2,2)/n2,2)/(n2-1)
	return num / (denom1 + denom2)

def MyFactorial(num):
	if num == 0:
		return 1

	fact = 1
	for x in range(1, num+1):
		fact = fact * x
	return fact
