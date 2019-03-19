from stateMachineV2 import State, HSM
from States import *
from GameObjects import Location

class warriorSMFactory():
    def __init__(self, objectManager, moveData=None):
        if moveData !=None:
            self.moveData = moveData
        else:
            self.moveData = MovementData()
        self.objectManager = objectManager
        self.statesCombat = {
                "checkRangeState"       :CheckRangeState("checkRangeState", self.objectManager),
                "damageTargetState"     :DamageTargetState("damageTargetState", self.objectManager),
                "castingState"          :CastingState("castingState", self.objectManager),
                "initialAttackState"    :InitialAttakState("initialAttackState", self.objectManager)
        }
        self.statesCombat['startingState'] = self.statesCombat['checkRangeState']

        self.statesGeneral = {
            "followPathState"   : FollowPathState("followPathState", self.objectManager, self.moveData),
            "walkingState"      : WalkingState('walkingState', self.objectManager, self.moveData),
            "clearAreaState"    : ClearAreaState("clearAreaState", self.objectManager, self.moveData),
            "combatState"       : self.createWarriorCombatSM(),
            "idleState"         : IdleState('idleState', self.objectManager, self.moveData)
        }

        self.statesGeneral['startingState'] = self.statesGeneral['followPathState']

    def createWarriorCombatSM(self):
        return HSM("combatState", self.objectManager, self.statesCombat)

    def createWarriorGeneralSM(self):
        return HSM('warriorGeneralHSM', self.objectManager, self.statesGeneral)



class CheckRangeState(State):
    def next(self):
        print("checking range")
        distance = 2
        player = self.objectManager.getPlayer()
        print("have player")
        if player.target():
            print("have target")
            if player.distanceToTarget() > distance:
                player.walkToTarget(player.target(), dis=distance)
                nxtState = self.name
                print("returning {}".format(nxtState))
                return nxtState
            else:
                print('Trying to target {}'.format(player.target()))
                player.turnCharacter(desiredTarget=player.target())
                return "damageTargetState"
        else:
            print("dont have target")
            return "clearAreaState"

class DamageTargetState(State):

    def __init__(self, name, objectManager):
        super().__init__(name, objectManager)
        self.initialAttack = False

    def next(self):
        player = self.objectManager.getPlayer()
        print("in damagetarget")
        if player.target() != None:
            print("player has target")
            if self.initialAttack == False:
                self.initialAttack = True
                return "initialAttackState"
            else:
                if player.rage() > 20 and player.target().healthPercent() > 0.20:
                    print("Player rage = {}".format(player.rage()))
                    if player.cast('HeroicStrike'):
                        return 'castingState'
                    else:
                        return 'checkRangeState'
            if player.target().health() == 0:
                self.initialAttack = False
                return "clearAreaState" #exit combat
            else:
                return "checkRangeState"

        self.initialAttack = False
        print("Dont have a target")
        return "clearAreaState"

class CastingState(State):

    def next(self):
        player = self.objectManager.getPlayer()
        if player.casting:
            spell = player.casting
        else:
            return "castingState"

        if (spell.castTime != None):
            if spell.castTime.completed():
                return "checkRangeState"
            else:
                return self.name
        else:
            return "checkRangeState"

class InitialAttakState(State):

    def next(self):
        player = self.objectManager.getPlayer()
        if player.target() != None:
            player.cast('Attack')
            return 'castingState'
