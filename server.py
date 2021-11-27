import socket
import os
import random
from _thread import *

MAP_WIDTH = 2000
MAP_HEIGHT = 2000
covers_count = 100

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
player_count = 0
try:
	ServerSocket.bind((host, port))
except socket.error as e:
	print(str(e))

#initialize map
covers = []
for i in range(covers_count):
	covers.append((random.randrange(MAP_WIDTH), random.randrange(MAP_HEIGHT), random.randrange(40, 80), random.randrange(40, 80)))
print('Waiting for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection):
	connection.send(str.encode(str(covers)))
	username = connection.recv(1024)
	connection.send(str.encode([player_count, random.randrange(MAP_WIDTH), random.randrange(MAP_HEIGHT)]))
	while True:
		data = connection.recv(2048)
		reply = 'Server Says: ' + data.decode('utf-8')
		if not data:
			break
		connection.sendall(str.encode(reply))
	connection.close()

while True:
	Client, address = ServerSocket.accept()
	player_count += 1
	print('Connected to: ' + address[0] + ':' + str(address[1]))
	start_new_thread(threaded_client, (Client, ))
	print('Number of Players: ' + str(player_count))
ServerSocket.close()