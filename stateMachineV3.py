# State transition table

# Current State		Condition		State transition

# MovingToNextLoc		attacked		combat
# combat				killed enemy	Recovering
# Recovering			health full		ClearArea
# ClearArea			Area Clear 		MovingToNextLoc


class State():

# 	init
# 	Enter 
# 	Exit 
# 	Execute

	def __init__(self, stateMachine):
		self.stateMachine = stateMachine
		self.objectManager = stateMachine.objectManager
		self.player = stateMachine.player

	def Enter(self):
		return
		#do things like change location ect
	def Exit(self):
		return
		#announce exit other things
	def Execute(self):
		return
		#main logic kill things walk ect or at least monitor
		#if they where initiated in enter

		#update state based on factors if state needs changing


class StateMachine():
# init
# Update
# ChangeState 
# RevertToPreviousState	
	def __init__(self, objectManager, stateMachine = None):
		self.objectManager = objectManager
		self.player = objectManager._player
		self.currentState = None
		self.previousState = None
		self.globalState = None
		self.stateMachine = None

	def Update(self):
		#run global logic then current state logic
		if self.globalState != None:
			self.globalState.Execute()
		if self.currentState != None:
			self.currentState.Execute()

	def ChangeState(self, newState):
		#check newState is valid state
		if not isinstance(newState, State):
			print('newState doesnt exist!!')

		#save prev
		self.previousState = self.currentState
		self.currentState.Exit()

		self.currentState = newState
		self.currentState.Enter()

	def RevertToPreviousState(self):
		self.ChangeState(self.previousState)








































