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
MEM_RELEASE = 0x00008000
#get functions from windll
OpenProcess = windll.kernel32.OpenProcess
GetWindowThreadProcessId = windll.User32.GetWindowThreadProcessId
ReadProcessMemory = windll.kernel32.ReadProcessMemory
WriteProcessMemory = windll.kernel32.WriteProcessMemory
VirtualProtectEx = windll.kernel32.VirtualProtectEx
VirtualAllocEx = windll.kernel32.VirtualAllocEx
VirtualFreeEx = windll.kernel32.VirtualFreeEx
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
    bytesWritten = create_string_buffer(5)
    if WriteProcessMemory(hprocess, paddress, byref(hookOpCodes), 5 ,byref(bytesWritten))== False:
        print("Write didnt work")
    VirtualProtectEx(hprocess, hookAddress, 5, curProtection, None)


#def Hook
def Hook(hprocess, hookAddress, jmpAddress, len, debug=False):
    #need at least 5 bytes to place a jmp
    if(len < 5):
        return False
    #setup protections
    curProtection = DWORD()
    if VirtualProtectEx(hprocess, hookAddress, len, PAGE_EXECUTE_READWRITE, byref(curProtection))==False:
        print("hook protection didnt work")
        return False
    relativeAddress = jmpAddress - hookAddress
    if debug :
        print("relative address as seen in hook {}".format(hex(relativeAddress)))
    hookAsm = assemble("jmp {}".format(hex(relativeAddress)))
    hookOpCodes = create_string_buffer(len)
    hookOpCodes[:] = hookAsm
    paddress = c_void_p(hookAddress)
    bytesWritten = create_string_buffer(len)
    if WriteProcessMemory(hprocess, paddress, byref(hookOpCodes), len,byref(bytesWritten))== False:
        print("Write didnt work")
    if debug:
        print(bytesWritten.value)
    VirtualProtectEx(hprocess, hookAddress,len, curProtection, None)

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



def InjectAndExecute(hprocess, caveContents, debug=False, debug_string='No Info'):
    #Magic Number
    endScene = 0x6B22279F
    hookAddress = endScene

    relativeReturnAddress = 0x0FFFFFFF
    flagAddress = 0x0FFFFFFF

    caveStart = '''
                pushfd\n
                pushad\n
                '''
    caveSetFlag ='''
                mov eax, {flagAddress}\n
                mov ebx, {value}\n
                mov [eax], ebx\n
                '''.format(flagAddress=hex(flagAddress), value = hex(0x00000001))
    caveEnd =   '''
                popad\n
                popfd\n
                mov edi, edi\n
                push ebp\n
                mov ebp, esp\n
                '''
    caveRtn = "jmp {}\n".format(hex(relativeReturnAddress))
    codecave = caveStart + caveContents + caveSetFlag + caveEnd + caveRtn
    codecave = assemble(codecave)

    #Allocate codecave memory
    caveAddress = VirtualAllocEx(hprocess, 0, len(codecave),MEM_COMMIT, PAGE_EXECUTE_READWRITE)
    #Allocate memory for complete flag
    flagAddress = caveAddress + len(codecave)
    VirtualAllocEx(hprocess, flagAddress, 4,MEM_COMMIT, PAGE_EXECUTE_READWRITE)
    #Calculate return address
    relativeReturnAddress = (hookAddress + 5) - caveAddress

    #fill in cave variables and complete cave contruciton
    caveRtn = "jmp {}\n".format(hex(relativeReturnAddress))
    caveSetFlag ='''
                mov eax, {flagAddress}\n
                mov ebx, {value}\n
                mov [eax], ebx\n
                '''.format(flagAddress=hex(flagAddress), value = hex(0x00000001))
    codecave = caveStart + caveContents + caveSetFlag + caveEnd + caveRtn
    codecave = assemble(codecave)

    if debug:
        print("flagAddress = {}".format(hex(flagAddress)))
        print("Codecave Address : %0x"%caveAddress)
        print("CodecaveBytes : {}".format(codecave))

    #Write codecave to memory
    pcaveAddress = c_void_p(caveAddress)
    caveBuffer = create_string_buffer(len(codecave))
    caveBuffer[:] = codecave
    if WriteProcessMemory(hprocess, pcaveAddress, byref(caveBuffer), len(codecave), None)== False:
        print("Write didnt work")
        return False

    #Hijack thread and hook endscene
    threadId = GetProcessThreadId(hprocess)
    thread = OpenThread(THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_SUSPEND_RESUME,False,threadId)
    SuspendThread(thread)
    Hook(hprocess, hookAddress, caveAddress, 5)
    ResumeThread(thread)

    #Poll complete flag until cave has executed
    while True:
        if memRead(hprocess, flagAddress) != 0:
            break
    if debug:
        print(debug_string)
        print("has been executed")
    #Restore hook
    SuspendThread(thread)
    unHook(hprocess, hookAddress)
    ResumeThread(thread)

    #deallocate memory
    VirtualFreeEx(hprocess, caveAddress, len(codecave), MEM_RELEASE)
    #free handles
    CloseHandle(thread)
    return True

def SetTarget(hprocess, desiredTarget):
    caveContents =      '''push {guid1}\n
                        push {guid2}\n
                        mov eax,0x493540\n
                        call eax\n'''.format(guid1 = hex(desiredTarget.getGuidUpper()), guid2= hex(desiredTarget.getGuidLower()))
    if InjectAndExecute(hprocess, caveContents):
        return True
    else:
        return False
