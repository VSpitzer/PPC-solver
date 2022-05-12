import numpy as np
from itertools import chain, combinations

class Problem:
	def __init__(self, Variables:int, Domains:list, Constraints:dict) :
		self.Variables = Variables #un entier n qui définie le nbr total de variables du pb
		self.Domains = Domains #un tableau de taille n : Domains[i]=liste des valeurs possibles de la variable i
		self.Constraints = Constraints #un dictionnaire : Constraint[(i,j)] = liste des contraintes qui lient i et j 
		
		
         
	def copie(self):
		obj=Problem(self.Variables, self.Domains.copy(), self.Constraints.copy())
		return obj

	#Ajoute une contrainte liée aux variables (i,j). c peut être défini par extension ou par intension
	def add_constraint(self, i:int, j:int, c, defined_by_intension=False):
		if not defined_by_intension :
			if not (i,j) in self.Constraints :
				self.Constraints[(i,j)]=c
			else :
				c1=self.Constraints[(i,j)]
				self.Constraints[(i,j)]=[x for x in c1 if (x in c)]
		else :
			if not (i,j) in self.Constraints :
				L=[(k,l) for k in self.Domains[i] for l in self.Domains[j]]
			else :
				L=self.Constraints[i,j]
			c=c.replace("i","k")
			c=c.replace("j","l")
			self.Constraints[(i,j)]=[(k,l) for (k,l) in L if bool(c)]

	def alldiff (self) :
		for i in range (self.Variables) :
			for j in range (self.Variables) :
				if not (i,j) in self.Constraints :
					c=[(k,l) for k in self.Domains[i] for l in self.Domains[j]]
				else :
					c=self.Constraints[(i,j)]
				self.Constraints[(i,j)]=[(k,l) for (k,l) in c if k!=l]

def reine(n) :
	D=[[i for i in range(n)] for j in range(n)]
	C={}
	for i in range (n) :
		C[i,i]=[(k,k) for k in range (n) ]
		for j in range(n) :
			if j!=i:
				C[i,j]=[(k,l) for k in range (n) for l in range (n) if (k!=l and abs(k-l)!=abs(j-i))]
	r=Problem(n,D,C)
	return r


#Importation d'un graphe à colorier ; n=nbr de sommets du graphe
def color(filename, n, nbr_color) :
    edges=np.loadtxt(filename,usecols=(1,2),comments=['c','p'], dtype=int)
    D=[[k for k in range (nbr_color)] for i in range (n)]
    C={}
    for (i,j) in edges :
        C[i-1,j-1]=[(k,l) for k in range(nbr_color) for l in range(nbr_color) if k!=l]
        C[j-1,i-1]=C[i-1,j-1]
    return Problem(n,D,C)

