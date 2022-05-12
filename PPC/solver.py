import numpy as np
import problems
import colorproblem
import time 
import random
import matplotlib.pyplot as plt

class ToSolve:

#Initialisation: nécessite seuelement l'objet Problem et les ordres sur les valeurs et variables
#Traite les ordres à l'initialisation, d_var ordre sur les variables, d_val l'ordre sur les valeurs, type liste

	def __init__(self, problem,d_var,d_val) :
		self.Problem=problem.copie()
		self.Solution=np.array([None]*problem.Variables)
		print(0)
		# Ordre sur les variables: changer leur entier d'identification, supprimer les contraintes superflues par rapport à l'ordre ( i>j ==> (i,j) supprimée) 

		self.Problem.Domains=[ problem.Domains[i] for i in d_var]
		print(1)
		for i in range(problem.Variables):
			for j in range(problem.Variables):
				if j<i and (i,j) in self.Problem.Constraints.keys():
					self.Problem.Constraints.pop((i,j))
				if j>=i:
					if (d_var[i],d_var[j]) in problem.Constraints.keys():
						self.Problem.Constraints[i,j]=problem.Constraints[d_var[i],d_var[j]].copy()
					elif (i,j) in self.Problem.Constraints.keys():
						self.Problem.Constraints.pop((i,j))
		print(2)
						
		# Ordre sur les valeurs: changer l'ordre des valeurs dans le domaine, le domaine sera traité dans cet ordre
		for i in range(problem.Variables):
			self.Problem.Domains[i]=[dv for dv in d_val if dv in self.Problem.Domains[i]]
		print(3)
		# Enregistrer les ordres pour retrouver le problème initial, la solution et faire des copies d'objet
		self.Ordre_val=d_val.copy()
		self.Ordre_var=d_var.copy()


	# Rends la solution dans l'ordre initial
	def get_solution(self):
		sol=np.array([None]*self.Problem.Variables)
		for i in range(len(sol)):
			sol[self.Ordre_var[i]]=self.Solution[i]
		return sol
		
	# Creation d'un nouvel objet identique à celui en instance
	def copie(self):
		rge=[i for i in range(self.Problem.Variables)]
		obj=ToSolve(self.Problem.copie(),rge,rge)

		obj.Ordre_var=self.Ordre_var.copy()
		obj.Ordre_val=self.Ordre_val.copy()
		obj.Problem=self.Problem.copie()
		obj.Solution=np.array(self.Solution)
		return obj
	
	# Copie de l'objet en instance sur celui en paramètre
	def rewind(self,memo):
		self.Problem=memo.Problem.copie()
		self.Solution=np.array(memo.Solution)
		
	def check_consistency(self,tup):
		(x,a)=tup
		id_rlv=[i for i in range(self.Problem.Variables) if self.Solution[i]!=None]
		for y in id_rlv:
			if (y,x) in self.Problem.Constraints.keys():
				if (self.Solution[y],a) not in self.Problem.Constraints[y,x]:
					return y
		return -1
			

# Algorithmes de Conflict_directed_backjump 
# L'algorithme présenté en cours avec l'iteration sur k est un bulshit total, en supprimant k on gagne énormément de temps. Gain grace a la formalisation orienté objet?

	def select_value_CBJ(self,i,D,J):
		for j in range(len(D[i])): 
			a=D[i][j]
			res=self.check_consistency((i,a))
			if res!=-1:
				if res not in J[i]:
					J[i].append(res)		
			else:
				D[i]=D[i][j+1:]
				self.Solution[i]=a
				return a
				
		return -1

	def conflict_directed_backjump(self,disp=True):
		init_time=time.time()
		cpt_backtrack=0
		
		i=0
		D=self.Problem.Domains.copy()
		J=dict()
		J[i]=[]	
		while i<self.Problem.Variables:
			x=self.select_value_CBJ(i,D,J)
			if x==-1:
				cpt_backtrack+=1
				ip=i
				if len(J[i])==0:
					print("Nombre de backtrack:", cpt_backtrack)
					end_time=time.time()
					print("Temps d'execution:",end_time-init_time)
					print("Problème inconsistant, pas de solution.")
					return False
				i=max(J[i])
				self.Solution[i:]=None
				J[i]+=[j for j in J[ip] if j!=i and j not in J[i]]
			else:
				i+=1
				if i>=self.Problem.Variables:
					break
					
				D[i]=self.Problem.Domains[i].copy()
				J[i]=[]
		
		if disp:
			print("Conflict_directed_backjump")
			print("Nombre de backtrack:", cpt_backtrack)
			end_time=time.time()
			print("Temps d'execution:",end_time-init_time)
			print("Solution:")
			print(self.get_solution())
			
		return True
		
	
# Algorithmes de Graph_based_backjump 

	def select_value(self,i,D):
		for a in D[i]: 
			if self.check_consistency((i,a))==-1:
				D[i]=[d_i for d_i in D[i] if d_i!=a]
				self.Solution[i]=a
				return a
		return -1

	def graph_based_backjump(self,disp=True):
		init_time=time.time()
		cpt_backtrack=0
		
		#Generation des ancêtres 
		anc={}
		for i in range(self.Problem.Variables): #imposer un ordre ou une heuristique?
			anc[i]=[]
			for j in range(i):
				if (j,i) in self.Problem.Constraints.keys():
					anc[i].append(j)
					
				
		i=0
		D=self.Problem.Domains.copy()
		l=anc.copy()	
		while i<self.Problem.Variables:
			x=self.select_value(i,D)
			
			if x==-1:
				cpt_backtrack+=1
				ip=i
				if len(l[i])==0:
				    print("Problème inconsistant, pas de solution.")
				    return False
				i=max(l[i])
				self.Solution[i:]=None
				l[i]+=[j for j in l[ip] if j!=i and j not in l[i]]
			else:
				i+=1
				if i>=self.Problem.Variables:
					break
				D[i]=self.Problem.Domains[i].copy()		
				l[i]=anc[i].copy()	
				
		if disp:
			print("Graph_based_backjump")
			print("Nombre de backtrack:", cpt_backtrack)
			end_time=time.time()
			print("Temps d'execution:",end_time-init_time)
			print("Solution:")
			print(self.get_solution())
			
			
		return True
	
# Algorithmes de backtrack avec AC3, AC4 et forward_check (FC) optionnels.

	def backtrack(self,AC3=False,AC4=False,FC=False):
	
		#Memoire de l'objet pour backtrack futur
		memo=self.copie()
	
		#Check si valide
		id_rlv=[i for i in range(self.Problem.Variables) if self.Solution[i]!=None]
		for i in range(len(id_rlv)):
			x=id_rlv[i]
			for j in range(len(id_rlv)):
				y=id_rlv[j]
				if (x,y) in self.Problem.Constraints.keys():
					if (self.Solution[x],self.Solution[y]) not in self.Problem.Constraints[x,y]:
						return False
					
		#Check si complet
		if len(id_rlv)==self.Problem.Variables:
			return True	
			
		#Instanciation d'une nouvelle variable					
		x=[i for i in range(self.Problem.Variables) if i not in id_rlv][0]
		for a in self.Problem.Domains[x]:
			self.Solution[x]=a
			
			#Propagation
			if FC:
				self.forward_check((x,a))
			if AC3: 
				self.AC3()
			if AC4:
				self.AC4()
			
			#Exploration des branches successeurs
			if self.backtrack(AC3,AC4,FC):
				return True
			
			#Echec et rewind, on efface le progrès effectué 
			self.rewind(memo)
				
		return False
			
# Algorithmes de forward check

	def forward_check(self,tup):
		(x,a)=tup
		for y in range(self.Problem.Variables):
			if self.Solution[y]==None:
				if x<y:
					tab=[b for (a,b) in self.Problem.Constraints[x,y]]
				else:
					tab=[b for (a,b) in self.Problem.Constraints[y,x]]
				self.Problem.Domains[y]=[e for e in self.Problem.Domains[y] if e in tab]
		return
		
		
# Algorithmes d'Arc-consistance
		
# AC3 apte à la symétrie: il n'est pas nécessaire de considérer les contraintes (p,q) et (q,p) de manière indépendante.
	def AC3(self):
		AC_solve=self.copie()
		#Prétraitement, élimination des contraintes superflues
		tab_sol=[]
		for i in range(self.Problem.Variables):
			a=AC_solve.Solution[i]
			if a!=None:
				AC_solve.Problem.Constraints[i,i]=[(a,a)]
				tab_sol.append(i)
		for i in tab_sol:
			for j in tab_sol:
				if i!=j and (i,j) in AC_solve.Problem.Constraints.keys():
					AC_solve.Problem.Constraints.pop((i,j))

		toTest=[]
		for (i,j) in AC_solve.Problem.Constraints.keys():
			toTest.append((i,j))
			while len(toTest)>0:
				(p,q)=toTest.pop()
				
				tab=[a for (a,b) in AC_solve.Problem.Constraints[p,q] if b in AC_solve.Problem.Domains[q]] 
				domain_tmp=[e for e in AC_solve.Problem.Domains[p] if e in tab]
				if len(domain_tmp)!=len(AC_solve.Problem.Domains[p]):
					AC_solve.Problem.Domains[p]=domain_tmp.copy()
					toTest+=[(z,w) for (z,w) in AC_solve.Problem.Constraints.keys() if w==p and z!=q]
				
				#Symétrie
				tab=[b for (a,b) in AC_solve.Problem.Constraints[p,q] if a in AC_solve.Problem.Domains[p]] 
				domain_tmp=[e for e in AC_solve.Problem.Domains[q] if e in tab]
				if len(domain_tmp)!=len(AC_solve.Problem.Domains[q]):
					AC_solve.Problem.Domains[q]=domain_tmp.copy()
					toTest+=[(z,w) for (z,w) in AC_solve.Problem.Constraints.keys() if w==q and z!=p]
		
		self.Problem.Domains=AC_solve.Problem.Domains.copy()
		return 
		
# AC4 peu apte à la symétrie, à cause du count[i,j,a]. Proposer un autre AC4 qui considère la symétrie?
	def init_AC4(self):
		count={}
		S={}
		Q=[]
		
		for (i,j) in self.Problem.Constraints.keys():
			for a in self.Problem.Domains[i]:
				total=0
				for b in self.Problem.Domains[j]:
					if (a,b) in self.Problem.Constraints[i,j]:
						total+=1
						if (j,b) in S.keys():
							S[j,b].append((i,a))
						else:
							S[j,b]=[(i,a)]
				count[i,j,a]=total
				if count[i,j,a]==0:
					self.Problem.Domains[i]=[e for e in self.Problem.Domains[i] if e!=a]
					Q.append((i,a))
					
			for a in self.Problem.Domains[j]:
				total=0
				for b in self.Problem.Domains[i]:
					if (b,a) in self.Problem.Constraints[i,j]:
						total+=1
						if (i,b) in S.keys():
							S[i,b].append((j,a))
						else:
							S[i,b]=[(j,a)]
				count[j,i,a]=total
				if count[j,i,a]==0:
					self.Problem.Domains[j]=[e for e in self.Problem.Domains[j] if e!=a]
					Q.append((j,a))
		return (Q,S,count)
		
	def AC4(self):
		AC_solve=self.copie()
		#Prétraitement, élimination des contraintes superflues
		tab_sol=[]
		for i in range(self.Problem.Variables):
			a=self.Solution[i]
			if a!=None:
				AC_solve.Problem.Constraints[i,i]=[(a,a)]
				tab_sol.append(i)
		for i in tab_sol:
			for j in tab_sol:
				if i!=j and (i,j) in AC_solve.Problem.Constraints.keys():
					AC_solve.Problem.Constraints.pop((i,j))
					
		(Q,S,count)=AC_solve.init_AC4()
		while len(Q)>0:
			(y,b)=Q.pop()
			if (y,b) in S.keys():
				for (x,a) in S[y,b]:
					count[x,y,a]-=1
					if count[x,y,a]==0 and a in AC_solve.Problem.Domains[x]:
						AC_solve.Problem.Domains[x]=[e for e in AC_solve.Problem.Domains[x] if e!=a]
						Q.append((x,a))
		
		self.Problem.Domains=AC_solve.Problem.Domains.copy()
		return
									

# Ordre canonique sous-optimal! trouver un meilleur ordre?
def solve_reine(n):
	tab_var=[i for i in range(n)]
	random.shuffle(tab_var)
	tab_val=[i for i in range(n)]
	random.shuffle(tab_val)
	print("-----------------------------------------------------------")
	print("ordres")
	print((tab_var,tab_val))


	toSolve=ToSolve(problems.reine(n),tab_var,tab_val)
	toSolve.conflict_directed_backjump()
	
	toSolve=ToSolve(problems.reine(n),tab_var,tab_val)
	toSolve.graph_based_backjump()


	return 
	



def solve_color (c,tab_var,tab_val) :
	toSolve=ToSolve(c,tab_var,tab_val)
	toSolve.AC3()
	print("fin AC")
