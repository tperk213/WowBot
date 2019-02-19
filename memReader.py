from ctypes import *
from ctypes.wintypes import *
from memoryManips import AdjustPrivilege, GetProcess, Hook, Injector
from GameObjects import *
import time

AdjustPrivilege("seDebugPrivilege")
hprocess = GetProcess()

my_object_manager = ObjectManager(hprocess)
my_object_manager.populateObjList()
my_object_manager.print()
my_object_manager.printUnitObjects()
player = my_object_manager.getPlayer()
#player.printHealth()
#player.printTarget()
endScene = 0x6B22279F
jmpAddress = 0x831d279f
inj = Injector(hprocess)
new_target = my_object_manager.getClosestTargetToPlayer()
print("Current target guid = {}".format(hex(player.target())))
print("new target = {}".format(hex(new_target.guid())))
print("new target upper GUID = {}".format(hex(new_target.guidUpper())))
print("new target lower Guid = {}".format(hex(new_target.guidLower())))
print("player pointer is {}".format(hex(player._address)))
player.passInjector(inj)

while True:
    player.SetTarget(new_target)
    player.turnCharacter(new_target)
    player.walkToTarget(new_target, dis=5)

    actions = [
                "CastSpellByName('Attack');",
                "CastSpellByName('Bloodrage');",
                "CastSpellByName('Battle Shout');"
                ]
    for action in actions:
        player.doString(action)
        time.sleep(2)
#SetTarget(hprocess, new_target)
#if(!isFacing(obj)):
#    turnToTarget(obj)
#Hook(hprocess, endScene, jmpAddress, 5)

#new_target = my_object_manager.getClosestTargetToPlayer()
#player.targetObject(new_target)
