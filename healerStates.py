
from stateMachineV2 import State, HSM
from States import *

class healerSMFactory():

        def __init__(self, objectManager):
            self.objectManager = objectManager
            self.statesCombat = {
                        "healTeamState"          : HealTeamState("healTeamState",self.objectManager),
                        "castingState"           : CastingState("castingState",self.objectManager),
                        "damageTargetState"      : DamageTargetState("damageTargetState", self.objectManager),
                        #"getTargetState"         : GetTargetState(self.objectManager)
            }
            self.statesCombat["startingState"] = self.statesCombat['healTeamState']

            self.statesGeneral = {
                        "followState"            : FollowState("followState", self.objectManager),
                        "combatState"            : self.createHealerCombatSM()
            }
            self.statesGeneral["startingState"] = self.statesGeneral['followState']


        def createHealerCombatSM(self):
            return HSM("healerCombatHSM", self.objectManager, self.statesCombat)

        def createHealerGeneralSM(self):
            return HSM("healerGeneralHSM", self.objectManager, self.statesGeneral)



class HealTeamState(State):

    def next(self):
        party = self.objectManager.getParty()
        player = self.objectManager.getPlayer()
        party['player'] = player
        # if leader below %50 heal
        if party['leader'].health() < (0.50 * party['leader'].maxHealth()):
            player.SetTarget(party['leader'])
            if player.cast('Lesser Heal'):
                return "castingState"
            else:
                print("couldnt cast lesser heal")
                return self.name
        #check if any players are hurt
        for name, partyPlayer in party.items():
            if partyPlayer.health() < (0.80 * partyPlayer.maxHealth()):
                player.SetTarget(partyPlayer)
                if player.cast('Lesser Heal'):
                    return "castingState"
                else:
                    print("couldnt cast lesser heal on {}".format(hex(partyPlayer.guid())))
                    return self.name

        #Damage party leader target
        print("party leader health percent {} ".format(party['leader'].healthPercent()))
        if party['leader'].target():
            print("party leader Target health percent {} ".format(party['leader'].target().healthPercent()))

        if party['leader'].target():
            if (party['leader'].healthPercent() < 0.99) and (party['leader'].target().healthPercent() < 0.99):
                print('returning damage target state')
                return "damageTargetState"
        else:
            return 'followState'


class CastingState(State):

    def next(self):
        player = self.objectManager.getPlayer()
        if player.casting:
            spell = player.casting
        else:
            return "castingState"

        if spell.castTime.completed():
            #print("Casting {} finished".format(spell.name))
            return "healTeamState"
        else:
            return self.name

class DamageTargetState(State):

    def next(self):
        print("in damage Target state")
        party = self.objectManager.getParty()
        player = self.objectManager.getPlayer()

        print("leader healthpercent {}".format(party['leader'].target().healthPercent()))
        print("mana percent {}".format(player.manaPercent()))

        if party['leader'].target():
            print('Party leader has target')
            if (party['leader'].target().healthPercent() < 0.7) and (player.manaPercent() > 0.8):

                player.SetTarget(party['leader'].target())
                if player.cast('Smite'):
                    return "castingState"
                else:
                    print("couldnt cast lesser Smite")
                    return self.name
        else:
            print("party leader doesnt have target")
            print("returning {}".format(self.name))
        print("returning {}".format(self.name))
        return self.name
