import time

class Timer():
    def __init__(self, length):
        self.finished = True
        self.startTime = time.time()
        self.length = length

    def start(self):
        self.startTime = time.time()
        self.finished = False

    def completed(self):
        if (time.time() - self.startTime) >= self.length:
            self.finished = True
        return self.finished

    def toGo(self):
        if(time.time() - self.startTime) <= self.length:
            return self.length - (time.time() - self.startTime)
        return 0

class SpellBook():

    def __init__(self):
        #self.spells = getSpellsPriest()
        self.spells = getSpellsWarrior()

        #self.priorityList = self.getPriorityList()

    # def getPriorityList(self):
    #     priorityList = [
    #         self.spells['Rend'],
    #         self.spells['HeroicStrike']
    #     ]
    #     return priorityList

class Spell():

    def __init__(self, args):
        self.name = args["name"]
        self.coolDown = args["coolDown"]
        self.cost = args["cost"]
        self.range = args["range"]
        if "castTime" in args:
            self.castTime = args["castTime"]
        else:
            self.castTime = None

    def cast(self, player):
        # print("player is {}".format(player
        casted = False
        print("trying to cast {}".format(self.name))
        if not player.globalCooldown.completed():
            print("Global cooldown not completed")
            return casted
        if not self.coolDown.completed():
            print("spell on cooldown")
            return casted
        #print("Player mana is {}".format(player.resource()))
        #print("Cost is {}".format(self.cost))
        #print("Distance is {}".format(player.distanceToTarget()))
        #print("spell range is {}".format(self.range))
        if(player.resource() >= self.cost and ((player.distanceToTarget() <= self.range) or (self.range == 0))):
            # print("spellname {}".format(self.name))
            player.doString("CastSpellByName('{}')".format(self.name))
            if self.castTime:
                self.castTime.start()
            self.coolDown.start()
            player.globalCooldown.start()
            print("Success casted")
            casted = True
        else:
            print("out of range or not enough mana")
            print("range = {} player at {}".format(self.range, player.distanceToTarget()))
            print("rage cost {} player rage".format(self.cost, player.rage()))
        return casted

    def done(self):
        if self.castTime:
            if not self.castTime.completed():
                return False
        return True

def getSpellsWarrior():
    battleShoutArgs = {
        "name"      : 'BattleShout',
        "coolDown"  : Timer(30),
        "cost"      : 10,
        "range"     : 0
    }
    heroicStrikeArgs = {
        "name"      : 'Heroic Strike',
        "coolDown"  : Timer(1),
        "cost"      : 15,
        "range"     : 3
    }
    rendArgs = {
        "name"      : 'Rend',
        "coolDown"  : Timer(10),
        "cost"      : 10,
        "range"     : 2
    }
    bloodrageArgs = {
        "name"      : 'Bloodrage',
        "coolDown"  : Timer(60),
        "cost"      : 0,
        "range"     : 0
    }
    attackArgs = {
        "name"      : 'Attack',
        "coolDown"  : Timer(1),
        "cost"      : 0,
        "range"     : 0
    }
    spells = {
                "BattleShout" : Spell(battleShoutArgs),
                "HeroicStrike" : Spell(heroicStrikeArgs),
                "Rend" : Spell(rendArgs),
                "Bloodrage" : Spell(bloodrageArgs),
                "Attack"    : Spell(attackArgs)
    }
    return spells


def getSpellsPriest():
    lesserHeal = {
        "name"      : 'Lesser Heal',
        "coolDown"  : Timer(0),
        "cost"      : 30,
        "range"     : 40,
        "castTime"  : Timer(1.5)
    }

    smite = {
        "name"      : 'Smite',
        "coolDown"  : Timer(0),
        "cost"      : 20,
        "range"     : 30,
        "castTime"  : Timer(1.5)
    }

    spells = {
                "Lesser Heal" : Spell(lesserHeal),
                "Smite"       : Spell(smite)
    }
    return spells
