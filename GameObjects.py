from ctypes import *
from ctypes.wintypes import *
from memoryManips import memRead, memSet, memStr, memReadUint64, Injector ,memReadFloat, convertFloatToHex, convertToFloat
import constants
import math
import numpy as np
import uptime

class Location():
    def __init__(self, obj=None, xPos=None, yPos=None, zPos=None):
        if obj != None:
            self.x = obj.X()
            self.y = obj.Y()
            self.z = obj.Z()
        else:
            self.x = xPos
            self.y = yPos
            self.z = zPos

class Object():

    def guid(self): return memReadUint64(self._hprocess, self._address +0x30)
    def guidLower(self): return memRead(self._hprocess, self._address +0x30)
    def guidUpper(self): return memRead(self._hprocess, self._address +0x34)
    def nextObjectAddress(self): return memRead(self._hprocess, self._address + 0x3c)
    def type (self): return memRead(self._hprocess, self._address + constants.ObjectMan.ObjType.value)

    def __init__(self, hprocess, address):
        self._hprocess = hprocess
        self._address = address
        self.accesors = {}
        self.inj = None


class UnitObject(Object):
    def descriptors(self):return memRead(self._hprocess, self._address + constants.ObjectMan.Descriptors.value)
    def factionId(self):return memRead(self._hprocess, self.descriptors() + constants.Descriptors.FactionId.value)
    def X(self):return memReadFloat(self._hprocess, self._address + constants.ObjectMan.UnitPosX.value)
    def Y(self):return memReadFloat(self._hprocess, self._address + constants.ObjectMan.UnitPosY.value)
    def Z(self):return memReadFloat(self._hprocess, self._address + constants.ObjectMan.UnitPosZ.value)
    def loc(self):return Location(self)
    def health(self):return memRead(self._hprocess, self.descriptors() + constants.Descriptors.Health.value)
    def target(self):return memReadUint64(self._hprocess, self.descriptors() + constants.Descriptors.TargetGuid.value)
    def movementState(self):return memRead(self._hprocess, self._address + constants.Descriptors.movementFlags.value)

    def __init__(self, baseObject=None, hprocess=None, address=None):
        if(baseObject):
            super().__init__(baseObject._hprocess, baseObject._address)
        else:
            super().__init__(hprocess, address)

    def printHealth(self):
        print("Health is %d" % self.health)

    def printTarget(self):
        print("Target Guid is %d" % self.target)

    def printFaction(self):
        print("Faction id is %d" % self.getFactionId())

    def getDistanceTo(self, obj=None, location=None):
        if obj != None:
            loc = obj.loc()
        else:
            loc = location
        try:
            return math.sqrt((loc.x - self.X())**2 + (loc.y - self.Y())**2 + (loc.z - self.Z())**2)
        except:
            print("couldnt get distance")
            return

    def printGuid(self):
        print("Guid is : {}".format(hex(self.guid())))


class Player(UnitObject):
    def facing(self):return memReadFloat(self._hprocess, self._address + constants.Player.Facing.value)

    def __init__(self, baseObject=None, hprocess=None, address=None):
        if(baseObject):
            super().__init__(baseObject)
            if baseObject.inj:
                self.passInjector(baseObject.inj)
        else:
            super().__init__(hprocess, address)


    def passInjector(self, inj):
        self.inj = inj

    def printFacing(self):
        print("facing {}".format(self.facing))

    def SetTarget(self, desiredTarget):
        caveContents =      '''push {guid1}\n
                            push {guid2}\n
                            mov eax,0x493540\n
                            call eax\n'''.format(guid1 = hex(desiredTarget.guidUpper()), guid2= hex(desiredTarget.guidLower()))
        if self.inj.InjectAndExecute(self._hprocess, caveContents):
            return True
        else:
            return False

    def SendMovementUpdate(self, opcode, timeStamp):

        caveContents =  '''
                        mov ecx, 0x{playerPointer:0x}\n
                        push 0x00000000\n
                        push 0x00000000\n
                        push 0x{opcode:0x}\n
                        push {timeStamp}\n
                        mov eax, 0x{SendMovementPacket:0x}\n
                        call eax\n
                        '''.format(playerPointer=self._address,opcode=opcode,timeStamp=convertFloatToHex(timeStamp),SendMovementPacket=constants.Functions.SendMovementPacket.value)
        self.inj.InjectAndExecute(self._hprocess, caveContents)

    def turnCharacter(self, desiredTarget=None, location=None):
        if desiredTarget != None:
            loc = desiredTarget.loc()
        if location != None:
            loc = location
        f = np.arctan2(loc.y - self.Y(), loc.x - self.X())

        #normalise
        if f<0.0:
            f = f + 2*np.pi
        if f> 2*np.pi:
            f = f - 2*np.pi
        toFace = f
        # print("playerPointer = {}".format(hex(self._address)))
        # print("ff = {}".format(convertFloatToHex(f)))
        # print("function = {}".format(hex(constants.Functions.SetFacing.value)))
        caveContents =  '''
                        mov ecx, {playerPointer}\n
                        add ecx, 0x9A8\n
                        push {ff}\n
                        mov eax, 0x{setFacing:000000008x}\n
                        call eax\n
                        '''.format(playerPointer=hex(self._address),ff=convertFloatToHex(toFace),setFacing=constants.Functions.SetFacing.value)
        #print("cave contents\n {}".format(caveContents))
        self.inj.InjectAndExecute(self._hprocess, caveContents)
        self.SendMovementUpdate(0xDA, uptime.uptime()*1000)

    def isFacing(self,desiredTarget=None, location = None):
        if desiredTarget != None:
            loc = desiredTarget.loc()
        if location != None:
            loc = location
        f = np.arctan2(loc.y - self.Y(), loc.x - self.X())
        #normalise
        if f < 0.0:
            f = f + (np.pi *2)
        if f > (np.pi*2):
            f = f - (np.pi *2)

        #print("f = {}".format(f))
        #print("facing = {}".format(self.facing))
        if f == self.facing:
            return True
        else:
            return False

    def walkToTarget(self, obj, dis=1):
        while self.getDistanceTo(obj=obj) > dis:
            print("distance :{}".format(self.getDistanceTo(obj=obj)))
            if self.isFacing(desiredTarget=obj) == False:
                self.turnCharacter(desiredTarget=obj)
            self.moveForward()
        self.moveStop()
        if self.isFacing(desiredTarget=obj) == False:
            self.turnCharacter(desiredTarget=obj)



    def walkToLocation(self, location=None, obj=None):
        if location and obj == None:
            print("Error need a location or obj to walk to")
            return False
        if obj != None:
            location = obj.loc()
        #debug
        while self.getDistanceTo(location=location) > 0.8:
            print("distance :{}".format(self.getDistanceTo(location=location)))
            if self.isFacing(location=location) == False:
                self.turnCharacter(location=location)
            self.moveForward()
            if obj != None:
                location = obj.loc()
        self.moveStop()

    def updateState(self):
        self = Player(self)

    def moveForward(self):
        #debug
        if self.movementState() != constants.MovementFlags.Forward.value:
            self.SetControlBit(constants.ControlBits.Front.value, 1)
            self.SetControlBit(constants.ControlBits.Back.value, 0)

    def moveStop(self):
        if self.movementState() != constants.MovementFlags.noFlag.value:
            self.SetControlBit(constants.ControlBits.Back.value, 0)
            self.SetControlBit(constants.ControlBits.Front.value, 0)

    def moveBackward(self):
        if self.movementState() != constants.MovementFlags.Back.value:
            self.SetControlBit(constants.ControlBits.Back.value, 1)
            self.SetControlBit(constants.ControlBits.Front.value, 0)


    def SetControlBit(self, bit, state):

        caveContents =  '''
                        mov eax, {getActive}\n
                        call eax\n
                        mov ecx, eax\n
                        push 0x0\n
                        push {uptime}\n
                        push {state}\n
                        push {bit}\n
                        mov eax, {setControl}\n
                        call eax\n
                        '''.format(
                                    getActive=hex(constants.Functions.CGInputControl__GetActive.value),
                                    uptime=hex(int(uptime.uptime()*1000)),
                                    state=hex(state),
                                    bit=hex(bit),
                                    setControl=hex(constants.Functions.CGInputControl__SetControlBit.value))
        #print("cave contents at send control bit\n {}".format(caveContents))
        self.inj.InjectAndExecute(self._hprocess, caveContents)

    def Attack(self):
        return

    def doString(self, str):

        paddress = memStr(self._hprocess, str)
        caveContents =  '''
                    mov edx, 0\n
                    mov ecx, {stringAddress}\n
                    mov eax, {doString}\n
                    call eax\n
                    '''.format(stringAddress = hex(paddress),
                                doString = hex(constants.Functions.DoString.value))

        self.inj.InjectAndExecute(self._hprocess, caveContents)


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
            if obj.type() == 3:
                self._unitObjList.append(UnitObject(obj))

    def populateObjList(self):
        self._objList.append(Object(self._hprocess, self._firstObject))
        curObj = self._objList[-1]
        self._numberOfObjects += 1
        while((curObj.nextObjectAddress() != 0) and (curObj.nextObjectAddress() % 2 == 0)):
            #Check is obj is player
            if curObj.guid() == self._playerGuid:
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
            if (self._player.getDistanceTo(obj) < closestObjDist) and obj.health() > 0:
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
