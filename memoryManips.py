from ctypes import *
from ctypes.wintypes import *
import win32process, win32security
import win32gui
import win32api
import win32con
import sys
import pyfasm

PROCESS_ALL_ACCESS = 0x1F0FFF
PAGE_EXECUTE_READWRITE = 0x40
PAGE_READWRITE = 0x04
MEM_COMMIT = 0x00001000
TH32CS_SNAPTHREAD = 0x04
THREAD_GET_CONTEXT = 0x08
THREAD_SUSPEND_RESUME = 0x02
THREAD_SET_CONTEXT = 0x010
#get functions from windll
OpenProcess = windll.kernel32.OpenProcess
GetWindowThreadProcessId = windll.User32.GetWindowThreadProcessId
ReadProcessMemory = windll.kernel32.ReadProcessMemory
WriteProcessMemory = windll.kernel32.WriteProcessMemory
VirtualProtectEx = windll.kernel32.VirtualProtectEx
VirtualAllocEx = windll.kernel32.VirtualAllocEx
GetProcessId = windll.kernel32.GetProcessId
CloseHandle = windll.kernel32.CloseHandle

#thread
CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
Thread32First = windll.kernel32.Thread32First
Thread32Next = windll.kernel32.Thread32Next
OpenThread = windll.kernel32.OpenThread
SuspendThread = windll.kernel32.SuspendThread
ResumeThread = windll.kernel32.ResumeThread

class THREADENTRY32(ctypes.Structure):
    _fields_ = [
    ('dwSize', ctypes.wintypes.DWORD),
    ('cntUsage', ctypes.wintypes.DWORD),
    ('th32ThreadId', ctypes.wintypes.DWORD),
    ('th32OwnerProcessId', ctypes.wintypes.DWORD),
    ('tpBasePri', ctypes.wintypes.LONG),
    ('tpDeltaPri', ctypes.wintypes.LONG),
    ('dwFlags', ctypes.wintypes.DWORD)
    ]

def AdjustPrivilege( priv ):
    flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    htoken =  win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    id = win32security.LookupPrivilegeValue(None, priv)
    newPrivileges = [(id, win32security.SE_PRIVILEGE_ENABLED)]
    win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)


def GetProcess():
    myWindow = win32gui.FindWindow(None,"World of Warcraft")
    _, pid = win32process.GetWindowThreadProcessId(myWindow)
    print("pid is ")
    print(pid)
    hprocess = HANDLE()
    hprocess = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    print(hprocess)
    return hprocess

def memReadUint64(hprocess, address):
    paddress = c_void_p(address)
    buffer = c_ulonglong()
    bufferSize = 8
    ReadProcessMemory(hprocess, paddress, byref(buffer), bufferSize, None)
    return buffer.value


def memRead(hprocess, address):
    paddress = c_void_p(address)
    buffer = DWORD()
    bufferSize = 4
    ReadProcessMemory(hprocess, paddress, byref(buffer), bufferSize, None)
    return buffer.value

def memSet(hprocess, address, desiredVal):
    #save old protection
    #deprotect memory
    oldProtection = DWORD()
    dwordDesiredVal = DWORD(desiredVal)
    bufferSize = 4 #size of DWORD in bytes
    paddress = c_void_p(address)
    if VirtualProtectEx(hprocess, paddress, bufferSize, PAGE_EXECUTE_READWRITE,byref(oldProtection)) == False:
        print("Virtual protect failed")
    #Write value
    if WriteProcessMemory(hprocess, paddress, byref(dwordDesiredVal), bufferSize) == False:
        print("WriteProcessMemory failed")
    #return protection to normal
    VirtualProtectEx(hprocess, paddress, bufferSize, oldProtection, None)

# Assemble from numonics
def assemble(mnemonics):
    if "use32" not in mnemonics:
        mnemonics ="use32\n{}".format(mnemonics)
    if type(mnemonics) == str:
        mnemonics = mnemonics.encode('ascii')

    data = pyfasm.assemble(mnemonics)
    return data
def unHook(hprocess, hookAddress):

    curProtection = DWORD()
    if VirtualProtectEx(hprocess, hookAddress, 5, PAGE_EXECUTE_READWRITE, byref(curProtection))==False:
        print("protection didnt work un hook")
        return False
    unHookAsm = assemble("mov edi, edi\npush ebp\nmov ebp, esp\n")
    hookOpCodes = create_string_buffer(len(unHookAsm))
    hookOpCodes[:] = unHookAsm
    paddress = c_void_p(hookAddress)
    #print("%0x"%paddress.value)
    bytesWritten = create_string_buffer(5)
    if WriteProcessMemory(hprocess, paddress, byref(hookOpCodes), 5 ,byref(bytesWritten))== False:
        print("Write didnt work")
    print(bytesWritten.value)
    VirtualProtectEx(hprocess, hookAddress, 5, curProtection, None)


#def Hook
def Hook(hprocess, hookAddress, jmpAddress, len):
    #need at least 5 bytes to place a jmp
    if(len < 5):
        return False
    #setup protections
    curProtection = DWORD()
    if VirtualProtectEx(hprocess, hookAddress, len, PAGE_EXECUTE_READWRITE, byref(curProtection))==False:
        print("hook protection didnt work")
        return False
    relativeAddress = jmpAddress - hookAddress
    print("relative address as seen in hook {}".format(hex(relativeAddress)))
    #str = "jmp {}".format(hex(0x005A17B6))
    #newstr = assemble(str)
    #print("new string is")
    #print(newstr)
    hookAsm = assemble("jmp {}".format(hex(relativeAddress)))
    #h1 = c_char(0xE9)
    #h2 = relativeAddress.to_bytes(4, byteorder ='big')

    hookOpCodes = create_string_buffer(len)
    #hookOpCodes[:] = [0x90,0x90,0x90,0x90,0x90]
    hookOpCodes[:] = hookAsm
    #print(hookOpCodes.value)
    #print(byref(hookOpCodes))
    # bhookOpCodes = bytes(hookOpCodes)
    # print(bhookOpCodes)
    # k = (c_char*len(hookOpCodes))(hookOpCodes)
    # print(k.value)
    paddress = c_void_p(hookAddress)
    #print("%0x"%paddress.value)
    bytesWritten = create_string_buffer(len)
    if WriteProcessMemory(hprocess, paddress, byref(hookOpCodes), len,byref(bytesWritten))== False:
        print("Write didnt work")
    print(bytesWritten.value)
    VirtualProtectEx(hprocess, hookAddress,len, curProtection, None)
#def GetEndscene
def GetProcessThreadId(hprocess):
    entry = THREADENTRY32()
    entry.dwSize = ctypes.sizeof(entry)
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if Thread32First(snapshot, byref(entry)) == True:
        pid = GetProcessId(hprocess)
        while (Thread32Next(snapshot, byref(entry))==True):
            if(entry.th32OwnerProcessId == pid):
                CloseHandle(snapshot)
                return entry.th32ThreadId
    CloseHandle(snapshot)
    return None
#def SetTarget

def SetTarget(hprocess, hookAddress, desiredTarget):
    # 5 is len of hook jmp codes
    relativeReturnAddress = 0x0FFFFFFF
    flagAddress = 0x0FFFFFFF

    #setupcodecave
    caveStart = '''pushfd\npushad\n'''
    caveSetFlag = '''mov eax, {flagAddress}\nmov ebx, {value}\nmov [eax], ebx\n'''.format(flagAddress=hex(flagAddress), value = hex(0x00000001))
    caveEnd =   '''popad\npopfd\nmov edi, edi\npush ebp\nmov ebp, esp\n'''
    caveRtn = "jmp {}\n".format(hex(relativeReturnAddress))
    caveContents =      '''push {guid1}\n
                        push {guid2}\n
                        mov eax,0x493540\n
                        call eax\n'''.format(guid1 = hex(desiredTarget.getGuidUpper()), guid2= hex(desiredTarget.getGuidLower()))
    codecave1 = caveStart + caveContents + caveSetFlag + caveEnd
    codecave1 = assemble(codecave1)
    codecave = caveStart + caveContents + caveSetFlag + caveEnd + caveRtn
    codecave = assemble(codecave)
    #codecave address = allocate memory for codecave
    address = VirtualAllocEx(hprocess, 0, len(codecave),MEM_COMMIT, PAGE_EXECUTE_READWRITE)
    flagAddress = address + len(codecave)
    print("flagAddress = {}".format(hex(flagAddress)))
    VirtualAllocEx(hprocess, flagAddress, 4,MEM_COMMIT, PAGE_EXECUTE_READWRITE)
    print("Codecave Address : %0x"%address)
    relativeReturnAddress = (hookAddress + 5) - address
    #fill in relative return address
    caveRtn = "jmp {}\n".format(hex(relativeReturnAddress))
    print("flagAddress = {}".format(hex(flagAddress)))
    caveSetFlag = '''mov eax, {flagAddress}\nmov ebx, {value}\nmov [eax], ebx\n'''.format(flagAddress=hex(flagAddress), value = hex(0x00000001))
    codecave = caveStart + caveContents + caveSetFlag + caveEnd + caveRtn
    codecave = assemble(codecave)
    print(codecave)
    paddress = c_void_p(address)
    caveBuffer = create_string_buffer(len(codecave))
    caveBuffer[:] = codecave
    if WriteProcessMemory(hprocess, paddress, byref(caveBuffer), len(codecave), None)== False:
        print("Write didnt work")

    #write codecave
    threadId = GetProcessThreadId(hprocess)
    thread = OpenThread(THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_SUSPEND_RESUME,False,threadId)

    #pause thread
    SuspendThread(thread)

    Hook(hprocess, hookAddress, address, 5)
    #unpause thread
    input("press enter to continue... ")
    ResumeThread(thread)
    while True:
        if memRead(hprocess, flagAddress) != 0:
            break
    SuspendThread(thread)

    #write hook(codecave address)
    unHook(hprocess, hookAddress)
    #unpause thread
    ResumeThread(thread)
    #poll codecave done flag
    #when done
    #pause thread
    #restore hook
    #unpause
    #retn
