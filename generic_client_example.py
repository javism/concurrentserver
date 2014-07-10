#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Javier Sánchez Monedero (jsanchezmonedero at gmail.com)
#
# This code is released under GNU GENERAL PUBLIC LICENSE V3
# http://www.gnu.org/licenses/gpl-3.0.html
#
# Implementa un servidor concurrente genérico muy básico. 
# En este ejemplo implementamos un servidor de multiplicación 
# que pedirá dos número al cliente y devolverá el resultado. 
# Si el cliente pasa un número menor o igual que cero pararemos el servidor. 

# This is a simple implementation of a generic concurrent server. 
# In this example a multiplication server is implemented. The server will
# request two numbers to the client and will send to it the result of the multiplication. 
# If a number less or equal to cero is received the server stops all the conection
# and thread and exit
# 

import socket
import time

class Client:
	buffer_size = 1024
	def __init__(self):
		self.__socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		
	def connect(self,host='localhost',port=8000):
		self.__socket.connect( (host, port ) )
		print 'Connected to ', host, ', port ',port

		data, server = self.__socket.recvfrom( Client.buffer_size )
		num = raw_input(data.strip())

		self.__socket.send(num)
		if float(num) <= 0.0:
			return self.close()

		data, server = self.__socket.recvfrom( Client.buffer_size )
		num = raw_input(data.strip())
		self.__socket.send(num)

		data, server = self.__socket.recvfrom( Client.buffer_size )

		print "Result is ", data
		
	def close(self):
		if self.__socket is not None:
			print 'Closing active socket...'
			time.sleep(1)
			self.__socket.close()
			self.__socket = None
			
	def __del__(self):
		return self.close()

def main():
	mi_cliente = Client()
	mi_cliente.connect()
	
	return 0

if __name__ == '__main__':
	main()
