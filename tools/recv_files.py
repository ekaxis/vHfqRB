'''
GNU General Public License v3.0

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
'''

import socket
import os
import sys
import time
import threading


def __recv(sock):
	buff_size = 4096
	data = b''
	while True:
		part = sock.recv(buff_size)
		data += part
		if len(part) < buff_size:
			break
	return data

def __recv_all(sock, size):
	buff_size = 4096
	data = b''
	while len(data) < size:
		part = sock.recv(buff_size)
		data += part
	return data

def listen_file(con, addr):
	print(f' [+] conexão aceita do host {addr[0]}')
	while True:
		mesg = __recv(con).decode('utf-8', errors='replace')
		print(f' [*] recv: {mesg}')
		if 'is_file' in mesg:
			name_file = mesg.split(':')[1]
			file_size = int(mesg.split(':')[2])
			if file_size == 0: file_size = 26
			con.send('ok'.encode())
			content = __recv_all(con, file_size)
			print(f' [*] recv: {len(content)} bytes.')
			file = open(name_file, 'wb')
			file.write(content)
			file.close()
			con.send('ok'.encode())
			con.close()
			break

if __name__ == '__main__':
	port = 8080
	hostname = '0.0.0.0'
	sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockt.bind((hostname, port))
	sockt.listen(5)
	print(f' /\\ escutando conexões...[{hostname}:{port}] :3')
	while True:
		con, addr = sockt.accept()
		threading.Thread(target=listen_file, args=(con, addr)).start()

