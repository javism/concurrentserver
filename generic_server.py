#!/usr/bin/python
# -*- coding: utf-8 -*-

# Implementa un servidor concurrente genérico muy básico. 
# En este ejemplo implementamos un servidor de multiplicación 
# que pedirá dos número al cliente y devolverá el resultado. 
# Si el cliente pasa un número menor o igual que cero pararemos el servidor. 

# This is a simple implementation of a generic concurrent server. 
# In this example a multiplication server is implemented. The server will
# request two numbers to the client and will send to it the result of the multiplication. 
# If a number less or equal to cero is received the server stops all the conection
# and thread and exit

import socket
import threading
import Queue
import signal
import sys
import os

class Server():
	buffer_size = 1024
	def __init__(self,host='localhost',port=8000,n_threads=4):
		"""Creates a server that will listen request in the port 'port'
		and using the interface pointed by 'localhost'. The server creates a 
		thread pool that will handle each request
		
		Keyword arguments:
		host -- host or ip address to listen to (default localhost)
		port -- port for the server (default 8000)
		n_threads - number of therads for the thread poool (default 4)
		
		"""
		
		#signal.signal(signal.SIGINT, self.signal_handler)
		
		if port <= 1024:
			print 'Port should be >=1024'
			return None

		self.__hostaddr = host
		self.__port = port
		
		self.__queue = Queue.Queue()
		
		print 'Queue ID', id(self.__queue)
		
		# Creamos la piscina de hilos y los iniciamos
		# Creates and initializes the thread pool
		self.__thread_pool = list()
		for i in range(n_threads): 
			c = ClientHandler(self,self.__queue)
			c.start()
			self.__thread_pool.append(c)
		
		# Start the server
		self.__start_server()
		
	def __start_server(self):
		"""
		Crea un socket pasivo, TCP, reutilizable (si se cierra el programa queda libre inmediatamente)
		
		Creates a pasive TCP socket so that it can be quickly reused 
		"""
	
		try:
			self.__main_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.__main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error:
			print 'Fail to create the socket' 
			os._exit(-1)			
		try:
			self.__main_socket.bind( ( self.__hostaddr, self.__port ) )
			self.__main_socket.listen(1)
		except socket.error as msg:
			print 'Cannot start to listen to at port ', self.__port,' probably the port is busy'
			self.__main_socket.close()
			self.__main_socket = None
			os._exit(-1)
			
	def signal_handler(self,signal, frame):
		print 'Ctrl+C pressed!'
		self.__stop_server()
		sys.exit(0)
		
	def stop_threads(self):
		"""Stop threads calling to the destructor"""
		for c in self.__thread_pool:
			del c
			
	def stop_server(self):
		print 'A thread as requested to finalize the server'
		return self.__stop_server()

	def __stop_server(self):
		self.stop_threads()

		# Stop the main socket
		# Optionally...
		#self.__main_socket.shutdown(socket.SHUT_WR)
		self.__main_socket.close()

	def __del__(self):
		print 'Server destroyer'
		return self.__stop_server()

	def loop(self):
		while True:
			print 'Blocking wait'
			try:
				conn, addr = self.__main_socket.accept()
			except KeyboardInterrupt:
				break
			print 'Conexión petition from ', addr
			self.__queue.put(conn)
		
		# Code only reachable after KeyboardInterrupt
		print 'Exit...'
		self.__stop_server()
		return
			
	def get_queue(self):
		return self.__queue
	
class ClientHandler(threading.Thread):
	def __init__(self,server,queue):
		threading.Thread.__init__(self)
		
		print 'Starting thread ', self.name
		
		self.__server = server
		self.__queue = queue
		self.__conn = None
	
	def run(self):
		
		while True:
			print 'Waiting...'
			self.__conn =  self.__queue.get()
			print 'Request handled by thread ', self.name
			self.handle_request()

    # Método específico del protocolo.			
	def handle_request(self):
		self.__conn.send('*** Wellcome to the multiplication server *** \ \n Please, introduce the first number: ')
		data = self.__conn.recv(Server.buffer_size)
		print 'data ',data
		
		# Exit if receive empty data
		if not data: return self.stop()
		
		n1 = float(data)
		print 'First number ', n1

		if n1 <= 0.0:
			print 'Close connections and exit'
			self.stop()
			self.__server.stop_server()
			return 
		self.__conn.send('Please, introduce the second number: ')
		
		data = self.__conn.recv(Server.buffer_size)
		if not data: return self.stop()
		
		n2 = float(data)
		print 'Second number ', n2
		r = str(n1*n2)
		print '\nResult ',r
		self.__conn.send(r)
		print "\nBye\n"
		self.stop()
		
	def stop(self):
		self.__conn.shutdown(socket.SHUT_WR)
		self.__conn.close()
		self.__conn = None

	def __del__(self):
		print 'Destroyer of thread ', self.name, ' was called'
		if self.__conn is not None:
			print 'Closing active socket' 
			self.stop()

def main():
	mi_servidor = Server()
	if mi_servidor is not None:
		mi_servidor.loop()
	
	return 0

if __name__ == '__main__':
	main()
	
	os._exit(0)
