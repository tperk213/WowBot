#include "windows.h"
#include <iostream>
#include <TlHelp32.h>

using namespace std;
//DWORD endSceneAddress = 0x73f1279f;
DWORD ReadMemWithOffset(HANDLE hprocess, DWORD baseAddress, DWORD offset){
	DWORD container;
	ReadProcessMemory(hprocess, (void *)(baseAddress + offset), &container, sizeof(DWORD), 0);
	return container;
}

DWORD GetProcessThreadId(HANDLE hprocess){
	THREADENTRY32 entry;
	entry.dwSize = sizeof(THREADENTRY32);
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);

	if(Thread32First(snapshot, &entry)==TRUE){
		DWORD pid = GetProcessId(hprocess);
		while (Thread32Next(snapshot, &entry)==TRUE){
			if(entry.th32OwnerProcessID == pid){
				CloseHandle(snapshot);
				return entry.th32ThreadID;
			}
		}
	}
	CloseHandle(snapshot);
	return NULL;
}

bool Hook(HANDLE hprocess, void * toHook, void * ourFunc, int len){
	if (len < 5)
		return false;

	DWORD curProtection;
	bool didProtectWork;
	didProtectWork = VirtualProtectEx(hprocess, toHook, len, PAGE_EXECUTE_READWRITE, &curProtection);
	BYTE hookOpCodes[5] = {
		0xE9,
		0x90,
		0x90,
		0x90,
		0x90
	};
	auto relativeAddress = (void *)((DWORD)ourFunc -(DWORD)toHook - 5);
	memcpy(&hookOpCodes[1], &relativeAddress,4);
	WriteProcessMemory(hprocess, toHook, hookOpCodes, 5, NULL);

	DWORD temp;
	VirtualProtectEx(hprocess, toHook, len, curProtection, &temp);

	return true;
}

void GetEndSceneAddress(){
	//inject codecave to save endscene
	//pause thread 
	//hook where to fin end scene
	DWORD whereToFindEndSceneAddress = 0x5A17B6;
	BYTE codeCaveHook[20]={
			//Save flags and registers
			0x60,				//pushad
			0x9C,				//pushfd
			

			//Restore flags and registers
			0x9D,				//popfd
			0x61,				//popad

			//retn to paused thread with out changing registers
			0x6A, 0x00,			//push origional epi
			0xC3				//retn
	};

	
}

bool callFunction(HANDLE hprocess, char * functionToCall){
	DWORD endSceneAddress = 0x73f1279f; //for now use get endscene address latter
	DWORD returnAddy = endSceneAddress + 5;
	BYTE codeCave[43] ={
		//save registers
		0x60,
		//call do string
		0xBA, 0x00, 0x00, 0x00, 0x00,	// mov edx 0
		0xB9, 0x00, 0x00, 0x00, 0x00,	// mov ecx 0 (put address of string here)
		0x50,							//push eax
		0xB8, 0xD0, 0x4C, 0x70, 0x00,	//mov eax, 704CDO (address of do string)
		0xFF, 0xD0,						//call eax
		0xB8, 0x00, 0x00, 0x00, 0x00,	//mov eax, move flag value to eax
		0x3E, 0xC7, 0x00, 0x01, 0x00, 0x00, 0x00, // set flag value to done
		0x58,							//pop eax
		0x61,						//restore registers
		0x8B, 0xFF,						//do overwritten asm
		0x55,
		0x8B,0xEC,
		0xE9, 0x00, 0x00, 0x00, 0x00								//retn
		//end call do string
	};
	DWORD doneFlag = 0x0;

	//Calculate space for remote string and codecave and doneFlag
	int flagLen = 4;
	int functionToCallNameLen = strlen(functionToCall) + 1;
	int caveLen = sizeof(codeCave);
	int fullLen = functionToCallNameLen + caveLen + flagLen;
	//Alocate space and get addresses
	auto remoteString = VirtualAllocEx(hprocess, 0, fullLen, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
	auto remoteCave = (LPVOID)((DWORD)remoteString + functionToCallNameLen);
	auto remoteFlag = (LPVOID)((DWORD)remoteCave + caveLen);

	//fill in params for cave
	auto relativeReturnAddy = (LPVOID)(returnAddy - (DWORD)remoteCave - 38 -5);
	memcpy(&codeCave[7], &remoteString, 4);
	memcpy(&codeCave[20], &remoteFlag, 4);
	memcpy(&codeCave[39], &relativeReturnAddy,4);

	//write string and cave to memory
	WriteProcessMemory(hprocess, remoteString, functionToCall, functionToCallNameLen,NULL);
	WriteProcessMemory(hprocess, remoteCave, codeCave, caveLen, NULL);
	WriteProcessMemory(hprocess, remoteFlag, &doneFlag, 4, NULL);

	int hookLen = 5; //from looking at debugger endscene local
	BYTE endSceneOrigional[5] = {
		0x8B, 0xFF,
		0x55,
		0x8B, 0xEC
	};

	//pause_thread
	DWORD threadId = GetProcessThreadId(hprocess);
	HANDLE thread = OpenThread(THREAD_GET_CONTEXT|THREAD_SUSPEND_RESUME|THREAD_SET_CONTEXT,false, threadId);
	//SuspendThread(thread);
	//using hprocess get thread handle and pause saving state
	Hook(hprocess, (void *)endSceneAddress, remoteCave, 5);

	//ResumeThread(thread);
	ReadProcessMemory(hprocess, (void *)remoteFlag, &doneFlag, sizeof(DWORD), 0);
	while(doneFlag == 0x0){
		ReadProcessMemory(hprocess, (void *)remoteFlag, &doneFlag, sizeof(DWORD), 0);
	}
	
	//dealocate codecave memory
	VirtualFreeEx(hprocess, remoteString, fullLen, MEM_RELEASE);
	
	//unhook endscene
	DWORD curProtection;
	VirtualProtectEx(hprocess, (void *)endSceneAddress, hookLen, PAGE_EXECUTE_READWRITE, &curProtection);
	WriteProcessMemory(hprocess, (void *)endSceneAddress, endSceneOrigional, hookLen, NULL);
	VirtualProtectEx(hprocess, &endSceneAddress, hookLen, curProtection, NULL);
	return true;
}

int main(){
	
	//consts
	DWORD offsetCurObjGuid = 0x30;
	DWORD offsetObjectManager = 0x00B41414;
	DWORD offsetPlayerGuid = 0xc0;
	DWORD offsetFirstObj = 0xac;
	DWORD offsetNextObj = 0x3c;
	DWORD offsetPlayerName = 0x827D88;
	DWORD offsetDescriptors = 0x8;
	DWORD offsetHealth = 0x58;

	
	// get wow window handle and pid
	HWND myWindow = FindWindow(NULL, L"World of Warcraft");
	DWORD pid;
	GetWindowThreadProcessId(myWindow, &pid);

	//Obtain handle to the process with desired access
	//PROCESS_VM_READ|PROCESS_VM_WRITE|PROCESS_VM_OPERATION
	HANDLE hprocess =  OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid); 
	DWORD newPid = GetProcessId(hprocess);
	//error checking
	if(hprocess == INVALID_HANDLE_VALUE){
		cout << "Couldn't get a valid process handle" << endl;
	}


	DWORD objMan;
	DWORD playerGuid;
	DWORD firstObj;
	DWORD nextObj;
	DWORD curObj;
	DWORD objGuid;
	DWORD desc;
	DWORD health;

	ReadProcessMemory(hprocess, (void *)offsetObjectManager, &objMan, sizeof(DWORD), 0);
	printf("Objman is at : %0x2\n", objMan);
	
	playerGuid = ReadMemWithOffset(hprocess, objMan, offsetPlayerGuid);
	printf("player GUID is :%d\n",playerGuid);

	curObj = ReadMemWithOffset(hprocess, objMan, offsetFirstObj);
	printf("first obj is at :%0x2\n", curObj);

	objGuid = ReadMemWithOffset(hprocess, curObj, offsetCurObjGuid);
	while(objGuid != playerGuid){
		nextObj = ReadMemWithOffset(hprocess, curObj, offsetNextObj);
		curObj = nextObj;
		objGuid = ReadMemWithOffset(hprocess, curObj, offsetCurObjGuid);
	}

	//Get player health
	desc = ReadMemWithOffset(hprocess, curObj, offsetDescriptors);
	health = ReadMemWithOffset(hprocess, desc, offsetHealth);
	printf("player health is :%d\n", health);


	// cast battle shout
	/*
	create a string with the lua function/logic pass it as a string
	ptr to do string function
	*/
	char * battleshout = "CastSpellByName('Battle Shout');\0";
	
	callFunction(hprocess, battleshout);

	//Start a thread to execute the code cave and therefore battleshout

	int wait;
	cin >> wait;
	printf("wait is :%d",wait);

	CloseHandle(hprocess);

	return 0;
}