import threading
import socket
import os
import sys
import time

port = 0


def __recv(sock):
	buff_size = 4096
	data = b''
	while True:
		part = sock.recv(buff_size)
		data += part
		if len(part) < buff_size:
			break
	return data


def try_conenct(hostname, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print(f'try connect {hostname}:{port}')
	sock.connect((hostname, port))
	return sock


while True:
	try:
		sock = try_conenct('0.0.0.0', port)
		while True:
			recv_mesg = sock.recv(1024).decode()
			print('recv:', recv_mesg)
			if '__exit' in recv_mesg:
				sock.sendall(b'__close.')
				break
			if '__recv_file' in recv_mesg:
				recv_file = recv_mesg.split(':')
				file = open(recv_file[2], 'wb')
				data = sock.recv(int(recv_file[1]))
				file.write(data)
				file.close()

			sock.sendall(f'{recv_mesg}'.encode())
		print('closing socket')
		sock.close()
		wait = threading.Thread(target=lambda: time.sleep(10))
		wait.start()
		wait.join()
	except:
		time.sleep(5)
