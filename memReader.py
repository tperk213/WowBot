from ctypes import *
from ctypes.wintypes import *
from memoryManips import AdjustPrivilege, GetProcess, Hook, SetTarget
from GameObjects import *

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
new_target = my_object_manager.getClosestTargetToPlayer()
print("Current target guid = {}".format(hex(player.getTargetByGuid())))
print("new target = {}".format(hex(new_target.getGuid())))
print("new target upper GUID = {}".format(hex(new_target.getGuidUpper())))
print("new target lower Guid = {}".format(hex(new_target.getGuidLower())))
SetTarget(hprocess, endScene, new_target)
#Hook(hprocess, endScene, jmpAddress, 5)

#new_target = my_object_manager.getClosestTargetToPlayer()
#player.targetObject(new_target)
