
from stateMachineV2 import State, HSM

#Bluepront for Factory
# class RoleSMFactory():
#
#         def __init__(self, objectManager):
#             self.objectManager = objectManager
#
#             #HSMs example below
#             self.statesCombat = {
#                         "healTeamState"          : HealTeamState("healTeamState",self.objectManager),
#                         "castingState"           : CastingState("castingState",self.objectManager),
#                         "damageTargetState"      : DamageTargetState("damageTargetState", self.objectManager),
#                         #"getTargetState"         : GetTargetState(self.objectManager)
#             }
#             self.statesCombat["startingState"] = self.statesCombat['healTeamState']
#
#             #regular states list
#             self.statesGeneral = {
#                         "followState"            : FollowState("followState", self.objectManager),
#                         "combatState"            : self.createHealerCombatSM()
#             }
#             self.statesGeneral["startingState"] = self.statesGeneral['followState']
#
#
#         def createHealerCombatSM(self):
#             return HSM("healerCombatHSM", self.objectManager, self.statesCombat)
#
#         def createHealerGeneralSM(self):
#             return HSM("healerGeneralHSM", self.objectManager, self.statesGeneral)


class FollowState(State):
    def next(self):
        party = self.objectManager.getParty()
        player = self.objectManager.getPlayer()

        #logic stay within certain radius of leader
        distance = 10 #yards
        if player.getDistanceTo(party['leader']) > distance:
            player.walkToTarget(party['leader'], distance)
            return self.name
        else:
            return "combatState"

class MovementData():
    def __init__(self, pathToFollow = None, grind=False, radius=30):
        self.targetLocation = None
        self.pathToFollow = pathToFollow
        self.grind = grind
        self.searchRadius = radius

class MovementState(State):

    def __init__(self, name, objectManager, moveData):
        super().__init__(name, objectManager)
        self.moveData = moveData

    def updateMoveData(self, moveData):
        self.moveData = moveData
class FollowPathState(MovementState):

    def next(self):

        player = self.objectManager.getPlayer()
        if self.moveData.pathToFollow != None :
            nextLocation = self.moveData.pathToFollow.pop(0)
            player.walkToLocation(location=nextLocation)
            self.moveData.targetLocation = nextLocation
            return "walkingState"
        else:
            print("couldnt find a path")
            return "idleState"

class WalkingState(MovementState):

    def next(self):
        player = self.objectManager.getPlayer()
        if player.getDistanceTo(location=self.moveData.targetLocation) > 1:
            return self.name
        else:
            if self.moveData.grind == False:
                return "followPathState"
            else:
                #workoutwaytopass location to clearArea
                return "clearAreaState"

class ClearAreaState(MovementState):

    def next(self):
        player = self.objectManager.getPlayer()

        target = self.objectManager.getClosestTargetToLocation(self.moveData.targetLocation, self.moveData.searchRadius)
        if target != None:
            player.SetTarget(target)
            return "combatState"
        else:
            #area clear
            return "followPathState"

class IdleState(MovementState):

    def __init__(self, name, objectManager, moveData):
        super().__init__(name, objectManager, moveData)
        self.nextState = None

    def next(self):
        if self.nextState == None:
            return self.name
        else:
            return self.nextState
