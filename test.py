import pyfasm

import numpy as np

targetY = 31
targetX = 32
Y=30
X=30
#conversion from radians to degrees
# convertRadiansToDegree = 360/(2*np.pi)
# convertDegreeToRadians =
# f = np.arctan2(targetY - Y, targetX-X)
# print(f)
# f = f/(2*np.pi)
# print(f)
# f = f*360
# print(f)
# input("enter")



def assemble(mnemonics):
    if "use32" not in mnemonics:
        mnemonics ="use32\n{}".format(mnemonics)
    if type(mnemonics) == str:
        mnemonics = mnemonics.encode('ascii')

    data = pyfasm.assemble(mnemonics)
    return data




from ctypes import *
from ctypes.wintypes import *
#Test for assemble
endSceneVar = 0xFFFFFFFF
relativeReturnAddress = 0xFFFFFFFF
doneFlag = 0xFFFFFFFF
add = 0x15e80008
ff = 0x3f5ce272
function = 0x7c6f30
codecave =  '''
            mov ecx, 0x17100008\n
            push 0x00000000\n
            push 0x00000000\n
            push 0xda\n
            push 0x4b82a4aa\n
            mov eax, 0x{SendMovementPacket:0x}\n
            call eax\n
            '''
print(codecave)
tempCodeCave = assemble(codecave)
print(tempCodeCave)
