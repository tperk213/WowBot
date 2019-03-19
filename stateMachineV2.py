
import time

GLOBAL = 0.01


class State():


    def __init__(self, name, objectManager):
        self.name = name
        self.objectManager = objectManager
        self.transitions = []

    def next(self):
        #check conditions in objectManager
        #set flags
        #return transitions[flags] #this is a state
        return

class HSM(State):

    def __init__(self, name, objectManager, states):
        super().__init__(name, objectManager)
        self.states = states
        self.startingState = states["startingState"].name
        self.curState = self.startingState
        self.nextState = self.startingState
        self.exNextState = self

    def next(self):
        self.nextState = self.states[self.curState].next()
        if self.nextState != self.curState:
            print("next state is {}".format(self.nextState))
        #leaving state machine
        if self.nextState not in self.states:
            print("leaving {}HSM for {}".format(self.name, self.nextState))
            print("becasue not in state list")
            self.curState = self.startingState
            return self.nextState
        #stay in stateMachine
        else:
            if self.curState != self.nextState:
                self.curState = self.nextState
        return self.name

    def updateMoveData(self, moveData):
        for _, state in self.states.items():
            try:
                state.updateMoveData(moveData)
            except:
                pass
