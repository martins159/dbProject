import socket
from _thread import *
import codecs
import os

def client_thread(connection):
	while True:

		data = connection.recv(1024).decode('UTF-8', errors = 'ignore')
		try:
			print(data)
		except Exception as e:
			print(e)
		if not data:
			break

server_socket = socket.socket()
host = 'haus.pump.lv'
port = 2000
ThreadCount = 0

try:
	server_socket.bind((host,port))
except socket.error as e:
	print(str(e))
print('waiting for connection')
server_socket.listen(5)

while True:
	client,address = server_socket.accept()
	print('connected to ' + address[0] + ' ' + str(address[1])
	start_new_thread(client_thread,(client,))
	ThreadCount += 1
	print('ThreadNumber ' + str(ThreadCount))
server_socket.close()
