# Kelly D Gawne & David Lopes
# This program listens for connections from a client computer
#RUN ME FIRST!

from twisted.internet import reactor, protocol, endpoints, defer
from twisted.internet.defer import DeferredQueue

HOST_PORT = 40017 #port to listen on for connections
num_players = 0

class GameConn(protocol.Protocol): #respond to data received
	def connectionMade(self):
		global num_players
		num_players+=1
		playerConnections[num_players] = self
		self.queue = DeferredQueue()
		self.transport.write("Connected to server as player " + str(num_players))
		print self.queue
		
	def connectionLost(self, reason):
		pass
		
	def dataReceived(self, data):
		print data
		self.queue.put(data)
		self.queue.get().addCallback(self.send_to_client)
		
	def send_to_client(self, data):
		pass
		#self.transport.write(data)
		
class GameConnFactory(protocol.ServerFactory):
	def buildProtocol(self,addr):
		return GameConn()


if __name__ == '__main__':
	playerConnections = []
	
	try:
		#listen on CMD_PORT for commands from work
		endpoint = endpoints.TCP4ServerEndpoint(reactor, HOST_PORT)
		endpoint.listen(GameConnFactory())

	except Exception as err:
		print "Unexpected error" + str(err)
	
	print "Listening for players on Port " + str(HOST_PORT) + "..."
	
	#Loop
	reactor.run()
