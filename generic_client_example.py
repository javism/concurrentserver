import socket
import time

class Client:
	buffer_size = 1024
	def __init__(self):
		self.__socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		
	def connect(self,host='localhost',port=8000):
		print 'Conectando a ', host, ' en el puerto ',port
		self.__socket.connect( ('localhost', 8000 ) )

		data, server = self.__socket.recvfrom( Client.buffer_size )
		num = raw_input(data.strip())

		self.__socket.send(num)
		if float(num) <= 0.0:
			return self.close()

		data, server = self.__socket.recvfrom( Client.buffer_size )
		num = raw_input(data.strip())
		self.__socket.send(num)

		data, server = self.__socket.recvfrom( Client.buffer_size )

		print "El resultado es ", data
		
	def close(self):
		if self.__socket is not None:
			print 'Cerrando socket activo'
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
