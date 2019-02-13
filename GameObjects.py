from ctypes import *
from ctypes.wintypes import *
from memoryManips import memRead, memSet, memReadUint64
import constants
import math

class Object():

    def __init__(self, hprocess, address):
        self._hprocess = hprocess
        self._address = address
        self._guid = memReadUint64(self._hprocess, self._address +0x30)
        self._guidLower = memRead(self._hprocess, self._address +0x30)
        self._guidUpper = memRead(self._hprocess, self._address +0x34)
        self._nextObjectAddress = memRead(self._hprocess, self._address + 0x3c)
        self._type = memRead(self._hprocess, self._address + constants.ObjectMan.ObjType.value)


    def nextObjectAddress(self):
        return self._nextObjectAddress

    def getType(self):
        #print("type is %d" % self._type)
        return self._type

    def getGuid(self):
        return self._guid

    def getGuidUpper(self):
        return self._guidUpper

    def getGuidLower(self):
        return self._guidLower



class UnitObject(Object):
    def __init__(self, baseObject=None, hprocess=None, address=None):
        if(baseObject):
            super().__init__(baseObject._hprocess, baseObject._address)
        else:
            super().__init__(hprocess, address)
        self._descriptors = memRead(self._hprocess, self._address + constants.ObjectMan.Descriptors.value)
        self._factionId = memRead(self._hprocess, self.getDescriptors() + constants.Descriptors.FactionId.value)
        self.posX = memRead(self._hprocess, self._address + constants.ObjectMan.UnitPosX.value)
        self.posY = memRead(self._hprocess, self._address + constants.ObjectMan.UnitPosY.value)
        self.posZ = memRead(self._hprocess, self._address + constants.ObjectMan.UnitPosZ.value)
        self.health = memRead(self._hprocess, self.getDescriptors() + constants.Descriptors.Health.value)
        self.target = memReadUint64(self._hprocess, self.getDescriptors() + constants.Descriptors.TargetGuid.value)

    def getDescriptors(self):
        return self._descriptors

    def getTargetByGuid(self):
        return self.target

    def getFactionId(self):
        return self._factionId

    def printHealth(self):
        print("Health is %d" % self.health)

    def printTarget(self):
        print("Target Guid is %d" % self.target)

    def printFaction(self):
        print("Faction id is %d" % self.getFactionId())

    def getDistanceTo(self, obj):
        try:
            return math.sqrt((obj.posX - self.posX)**2 + (obj.posY - self.posY)**2 + (obj.posZ - self.posZ)**2)
        except:
            print("couldnt get distance")
            return

    def printGuid(self):
        print("Guid is : {}".format(hex(self.getGuid())))


class Player(UnitObject):
    def __init__(self, baseObject=None, hprocess=None, address=None):
        if(baseObject):
            super().__init__(baseObject)
        else:
            super().__init__(hprocess, address)

class ObjectManager():

    def __init__(self,hprocess):
        self._hprocess = hprocess
        self._address = memRead(self._hprocess, 0x00B41414)
        self._playerGuid = memRead(self._hprocess, self._address + 0xc0)
        self._firstObject = memRead(self._hprocess, self._address + 0xac)
        self._objList = []
        self._numberOfObjects = 0
        self._unitObjList = []
        self._player = ''

    def _populateUnitObjList(self):
        for obj in self._objList:
            if obj.getType() == 3:
                self._unitObjList.append(UnitObject(obj))

    def populateObjList(self):
        self._objList.append(Object(self._hprocess, self._firstObject))
        curObj = self._objList[-1]
        self._numberOfObjects += 1
        while((curObj.nextObjectAddress() != 0) and (curObj.nextObjectAddress() % 2 == 0)):
            #Check is obj is player
            if curObj.getGuid() == self._playerGuid:
                self._player = Player(curObj)
            #Add obj to object list set cur obj to next obj
            self._objList.append(Object(self._hprocess, curObj.nextObjectAddress()))
            curObj = self._objList[-1]
            self._numberOfObjects += 1
        self._populateUnitObjList()

    def printUnitObjects(self):
        for obj in self._unitObjList:
            obj.printGuid()

    def print(self):
        print("ObjMan base Address = %0x" % (self._address))
        print("Number of Objects = %d" % self._numberOfObjects)
        print("Number of UnitObj = %d" % len(self._unitObjList))

    def getClosestTargetToPlayer(self):
        closestObjDist = 0x0FFFFFFF
        closestObj = ''
        for obj in self._unitObjList:
            if (self._player.getDistanceTo(obj) < closestObjDist) and obj.health > 0:
                closestObj = obj
                closestObjDist = self._player.getDistanceTo(obj)
        return closestObj
        #getDistanceBetweenObjects and player object
        #find closest object that isnt the player
        #if health > 0 target

    def getPlayer(self):
        return self._player

if __name__ =="__main__":
    my_object_manager = ObjectManager()
    my_object_manager.print()
