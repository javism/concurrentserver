#!/usr/bin/python
# -*- coding: utf-8 -*-

# Implementa un servidor concurrente genérico. 
# En este ejemplo implementamos un servidor de multiplicación 
# que pedirá dos número al cliente y devolverá el resultado. 
# Si el cliente pasa un número menor o igual que cero pararemos el servidor. 

import socket
import threading
import Queue
import signal
import sys
import os

class Server():
	buffer_size = 1024
	def __init__(self,host='localhost',port=8000,n_threads=4):
		"Inicializa el socket principal que aceptará conexiones"
		#threading.Thread.__init__(self)
		
		#signal.signal(signal.SIGINT, self.signal_handler)
		
		if port <= 1024:
			print 'Introduce un puero mayor que 1024'
			return None

		self.__hostaddr = host
		self.__port = port
		
		self.__queue = Queue.Queue()
		
		print 'ID cola', id(self.__queue)
		
		# Creamos la piscina de hilos y los iniciamos
		self.__thread_pool = list()
		for i in range(n_threads): 
			c = ClientHandler(self,self.__queue)
			c.start()
			self.__thread_pool.append(c)
		
		# Iniciamos el servidor		
		self.__start_server()
		
	def __start_server(self):
		"Crea un socket pasivo, TCP, reutilizable (si se cierra el programa queda libre inmediatamente)"
		try:
			self.__main_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.__main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error:
			print 'No se pudo crear el socket' 
			os._exit(-1)
			#sys.exit(-1)
			
		try:
			self.__main_socket.bind( ( self.__hostaddr, self.__port ) )
			self.__main_socket.listen(1)
		except socket.error as msg:
			print 'No se pudo iniciar el socket de escucha porque el puerto \
					estaba ocupado'
			self.__main_socket.close()
			self.__main_socket = None
			os._exit(-1)
			#sys.exit(-1)

	def signal_handler(self,signal, frame):
		print 'Has presionado Ctrl+C!'
		sys.exit(0)
			
	def stop_server(self):
		print 'Petición de finalización al servidor desde un hilo'
		return self.__stop_server()

	def __stop_server(self):
		# Para los clientes activos
		for c in self.__thread_pool:
			del c

		# Para el socket principal
		#self.__main_socket.shutdown(socket.SHUT_WR)
		self.__main_socket.close()

	def __del__(self):
		print 'Destructor llamado'
		return self.__stop_server()

	def loop(self):
		while True:
			print 'Esperamos bloqueados'
			try:
				conn, addr = self.__main_socket.accept()
			except KeyboardInterrupt:
				break
			print 'Conexión recibida de ', addr
			self.__queue.put(conn)
		
		print 'Saliendo...'
		self.__stop_server()
		return
			
	def get_queue(self):
		return self.__queue
	
class ClientHandler(threading.Thread):
	def __init__(self,server,queue):
		threading.Thread.__init__(self)
		
		print 'Iniciando hilo ', self.name
		
		self.__server = server
		self.__queue = queue
		self.__conn = None
	
	def run(self):
		
		#while not self.__queue.empty():
		while True:
			print 'Esperando...'
			self.__conn =  self.__queue.get()
			print 'Petición atendida desde el hilo ', self.name
			self.handle_request()

    # Método específico del protocolo.			
	def handle_request(self):
		self.__conn.send('*** Bienvenido/a al servidor de multiplicación *** \ \n Dame el primer número: ')
		data = self.__conn.recv(Server.buffer_size)
		print 'data ',data
		
		if not data: return self.stop()
		
		n1 = float(data)
		print "Introducido ", n1

		if n1 <= 0.0:
			print "Cerramos y salimos"
			self.stop()
			self.__server.stop_server()
			return 
		self.__conn.send('Dame el segundo número: ')
		
		data = self.__conn.recv(Server.buffer_size)
		if not data: return self.stop()
		
		n2 = float(data)
		print "Introducido ", n2
		r = str(n1*n2)
		print "\nEl resultado es ",r
		self.__conn.send(r)
		print "\nADIÓS\n"
		self.stop()
		
	def stop(self):
		self.__conn.shutdown(socket.SHUT_WR)
		self.__conn.close()
		self.__conn = None

	def __del__(self):
		print 'Destructor del hilo ', self.name, ' llamado'
		if self.__conn is not None:
			print 'Cerrando socket activo' 
			self.stop()

def main():
	mi_servidor = Server()
	if mi_servidor is not None:
		mi_servidor.loop()
	
	return 0

if __name__ == '__main__':
	main()
	
	os._exit(0)
