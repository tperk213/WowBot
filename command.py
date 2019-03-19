from ctypes import *
from ctypes.wintypes import *
from memoryManips import AdjustPrivilege, GetProcess, Hook, Injector, GetProcessA
from GameObjects import *
from stateMachine import *
import subprocess
import time
import threading
from healerStates import healerSMFactory


AdjustPrivilege("seDebugPrivilege")
runningInstances = {}
selectedInstance = None
modes = [
        "Idle",
        "AcceptInv",
        "InviteOthers",
        "Grind",
        "Heal"
        ]


def tankSetup():
    return

def healerSetup():
    healerFactory = healerSMFactory(my_object_manager)
    mySM = healerFactory.createHealerGeneralSM()

setups = {
            "Tank"          : tankSetup,
            "Healer"        : healerSetup,
}

class Instance():
    def __init__(self, hprocess):
        self.my_object_manager = None
        self.player = None
        self.setup = None
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.runSM)
        self.thread.start()
    def stop(self):
        self.thread.do = False
        self.thread.join()

    def initiateObjectManager(self):
        self.my_object_manager = ObjectManager(hprocess)
        self.my_object_manager.populateObjList()
        self.my_object_manager.printUnitObjects()
        self.player = my_object_manager.getPlayer()

    def runSM():
        t = threading.currentThread()
        while getattr(t, "do", True):
            mySM.next()
            time.sleep(0.5)
        print("stopping")


def helper(dict):
    for keys, items in dict.items():
        print(keys)

def openWow():
    name = input("Name for instance eg. Healer")
    path = "C:\\Users\\Public\\Games\\World of Warcraft-Classic\\WoW.exe"
    process = subprocess.Popen(path)
    hprocess = GetProcessA(process.pid)
    runningInstances[name] = Instance(hprocess)

def selectInstance():
    print("Current instances of Wow running:")
    for key, val in runningInstances.items():
        print(key)
    selection = input("select instance : ")

    if selection in runningInstances:
        selectedInstance = runningInstances[selection]
        print("{} selected".format(selection))
        return
    else:
        print("selection not available")


def changeMode():
    print("Modes available:")
    print(modes)

def setupInstance():
    print('Setups Available:')
    print(setups.keys())
    desiredSetup = input("select Setup... ")
    if desiredSetup in setups:
        setups[desiredSetup]()

def currentInstance():
    print("Current instance {}".format(selectedInstance))

commands = {
            "h"                 : helper,
            "Open Wow"          : openWow,
            "Select Instance"   : selectInstance,
            "Current Instance"  : currentInstance,
            "Setup Instance"    : setupInstance,
            "Change Mode"       : changeMode,
}

print("Welcome To Bot Control Center")

while True:
    command = input("Please input a comand (h for help)")
    if command == 'h':
        commands[command](commands)
    else:
        commands[command]()



# healerFactory = healerSMFactory(my_object_manager)
# mySM = healerFactory.createHealerGeneralSM()
#
# # player.doString("CastSpellByName('{}')".format('Lesser Heal'))
# def testSM():
#     t = threading.currentThread()
#     while getattr(t, "do", True):
#         mySM.next()
#         time.sleep(0.5)
#     print("stopping")
#
# t = threading.Thread(target=testSM)
# t.start()
# input("Stop following?")


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
