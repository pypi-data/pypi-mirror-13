'''created by George kapoya
date: 07-02-16
'''

class Person:
	
#constructor
  def __init__(self):

  	print("class is created and initialised")
  def setFullName(self,firstName,lastName):
     self.firstName = firstName
     self.lastName = lastName
  def printFullName(self):
     	print(self.firstName +' '+self.lastName)
         
  def printNames(self, count,names):

     while count < len(names): 
          print("Name: "+names[count])
          if names[count] == "vero":
             print("name found "+names[count])
          else:
          	 print("could not find a match")
          count = count + 1