from ctypes import *
from ctypes.wintypes import *
from memoryManips import AdjustPrivilege, GetProcess, Hook, Injector, GetProcessA
from GameObjects import *
from stateMachine import *
import subprocess
import time
import threading
from healerStates import healerSMFactory
from warriorGrindStates import warriorSMFactory
from States import MovementData

AdjustPrivilege("seDebugPrivilege")

#hprocess = GetProcess()
# path = "C:\\Users\\Public\\Games\\World of Warcraft-Classic\\WoW.exe"
# pid1 = subprocess.Popen(path)
hprocess = GetProcessA(3544)

input("Login then press enter")
#setup object manager
my_object_manager = ObjectManager(hprocess)
my_object_manager.populateObjList()
my_object_manager.printUnitObjects()
player = my_object_manager.getPlayer()

#healerFactory = healerSMFactory(my_object_manager)
#mySM = healerFactory.createHealerGeneralSM()
warriorFactory = warriorSMFactory(my_object_manager)
mySM = warriorFactory.createWarriorGeneralSM()

# player.doString("CastSpellByName('{}')".format('Lesser Heal'))
def testSM():
    t = threading.currentThread()
    getPath = True
    while getattr(t, "do", True):
        if getPath and getattr(t, "path") != None:
            path = getattr(t, "path")
            getPath = False
            moveData = MovementData(pathToFollow = path, grind=True, radius=50.1)
            mySM.updateMoveData(moveData)
            mySM.states['idleState'].nextState = "followPathState"
        mySM.next()
        time.sleep(0.5)
    print("stopping")

t = threading.Thread(target=testSM)
t.path = None
t.do = True
t.start()
path = [
        Location(xPos=-130.0, yPos=-1056.1, zPos=46.4),
        Location(xPos=-69.0, yPos=-1037.1, zPos=57.4),
        #Location(xPos=1865.3, yPos=1481.2, zPos=87.0),
        #Location(xPos=1842.3, yPos=1467.2, zPos=89.0)
]
input("start following Path?")
t.path = path
t.join()

input("stop?")
t.do = False
t.join()

input("stop?")

#player1.doString('InviteByName("Gregtime")')
# print("Player 1 guid = {}".format(hex(my_object_manager1._playerGuid)))
#
# my_object_manager2 = ObjectManager(procs[0])
# my_object_manager2.populateObjList()
# #my_object_manager2.print()
# #my_object_manager2.printUnitObjects()
# player2 = my_object_manager2.getPlayer()
# #player2.doString('AcceptGroup()')
# print("Player 1 has {} health and should be leader".format(player1.health()))
# print("Player 2 has {} health and shouldnt be leader".format(player2.health()))
# print("Leader Guid is {}".format(hex(my_object_manager2.leaderGuid())))
# print("geting leader health from player 2 perspective : {}".format(my_object_manager2.leader().health()))

#player.printHealth()
#player.printTarget()Guid








# print("Current target guid = {}".format(hex(player.target())))
# print("new target = {}".format(hex(new_target.guid())))
# print("new target upper GUID = {}".format(hex(new_target.guidUpper())))
# print("new target lower Guid = {}".format(hex(new_target.guidLower())))
# print("player pointer is {}".format(hex(player._address)))
# player.cast('Attack')

# print("player location {}".format(hex(player._address)))
# print("Target location {}".format(hex(player.target()._address)))
# print("faction = {}".format(player.target().factionId()))

# stateMachine = StateMachine(my_object_manager)
# while not stateMachine.findEnemy():
#     time.sleep(0.0001)
# print("Found Enemy")
# while not stateMachine.engage():
#     time.sleep(0.0001)
# print("Engaged")
#
# while not stateMachine.generalCombat():
#     time.sleep(0.0001)
# print("target dead")


#SetTarget(hprocess, new_target)
#if(!isFacing(obj)):
#    turnToTarget(obj)
#Hook(hprocess, endScene, jmpAddress, 5)

#new_target = my_object_manager.getClosestTargetToPlayer()
#player.targetObject(new_target)
