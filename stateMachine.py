
import time
# class State():
#     def __init__(actions, conditions, posibleNextStates):
#         self.actions = actions
#         self.conditions = conditions
#         self.posibleNextStates = posibleNextStates
#
#     def run(self):
#         self.checkConditions()
#         self.performActions()
#         self.transitionToNextState()
#
#     def checkConditions(self):

class StateMachine():

    def __init__(self, objectManager):
        self.objectManager = objectManager
        self.player = self.objectManager.getPlayer()

    def findEnemy(self):

        #actions
        new_target = self.objectManager.getClosestTargetToPlayer(debug=True)
        print(hex(new_target.guid()))
        self.player.SetTarget(new_target)
        self.player.turnCharacter(new_target)
        while not self.player.target():
            time.sleep(0.01)
        if self.player.target().guid() == new_target.guid():
            return True
        print("player target isnt new target")
        print("player target is {}".format(hex(self.player.target().guid())))
        print("new target is {}".format(hex(new_target.guid())))

    def engage(self):
        target = self.player.target()
        print("target is {}".format(target))
        if not self.player.isFacing(desiredTarget=target):
            self.player.turnCharacter(desiredTarget=target)

        self.player.walkToTarget(target)
        self.player.cast('Attack')
        self.player.cast('Bloodrage')
        self.player.cast('BattleShout')

        return True


    def generalCombat(self):
        target = self.player.target()
        while target.health() > 0:
            #positioning
            if not self.player.isFacing(desiredTarget=target):
                self.player.turnCharacter(desiredTarget=target)
            if self.player.distanceToTarget() > 3:
                self.player.walkToTarget(target)
            if self.player.distanceToTarget() < 1:
                self.player.moveBackward()
            if self.player.distanceToTarget() > 1 and self.player.distanceToTarget() < 1.5:
                self.player.moveStop()
            #combat
            self.player.castBestSpell()
        return True
