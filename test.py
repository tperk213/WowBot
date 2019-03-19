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



print("Player X {}".format(player.X()))
print("Player Y {}".format(player.Y()))
print("Player Z {}".format(player.Z()))
