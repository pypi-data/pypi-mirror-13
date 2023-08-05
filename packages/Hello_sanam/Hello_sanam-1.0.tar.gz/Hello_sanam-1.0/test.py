class Person:
        def __init__(self):
                self.name = ''
	def setName(self, name):
		self.name = name
	def getName(self):
		return self.name
	def greet(self):
		print "Hello, world! I'm %s." % self.name
