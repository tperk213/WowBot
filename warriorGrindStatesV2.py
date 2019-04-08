from stateMachineV3 import State, StateMachine
from GameObjects import Location

def warriorSMFactory(objectManager):
    sM = StateMachine(objectManager)
    sM.currentState = IdleState(sM)
    return sM

class MoveToNextLocationState(State):
    
    def Enter(self):
        print("Entering MoveToNextLocation State")
        #clear target maybe
        #initiate walk to next location
        if self.player.moveData != None:
            if len(self.player.moveData.pathToFollow) < 1:
                self.stateMachine.ChangeState(IdleState(self.stateMachine))
                return 
            #get next location from que
            nextLocation = self.player.moveData.pathToFollow.pop(0)
            #set target location to nextLocatin
            self.player.moveData.targetLocation = nextLocation 
        else:
            print("couldnt find a path")
            self.stateMachine.ChangeState(IdleState(self.stateMachine))

    def Execute(self):
        
        location = self.player.moveData.targetLocation
        if self.player.getDistanceTo(location=location) > 0.8:
            print("distance :{}".format(self.player.getDistanceTo(location=location)))
            if self.player.isFacing(location=location) == False:
                self.player.turnCharacter(location=location)
            self.player.moveForward()
        else:
            print('Arived at location')
            self.stateMachine.ChangeState(MoveToNextLocationState(self.stateMachine))    

    def Exit(self):
        print('Exiting MoveToNextLocation State')
        self.player.moveStop()

class IdleState(State):

    def Enter(self):
        print("entering IdleState")

    def Execute(self):
        if self.player.moveData != None and len(self.player.moveData) >= 1:
            print('have movement data')
            self.stateMachine.ChangeState(MoveToNextLocationState(self.stateMachine))
        else:
            print('player has no movement data')    

    def Exit(self):
        print('Exiting Idle State')