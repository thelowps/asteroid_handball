#Kelly D Gawne & David Lopes
#	Connects to server and draws shit

from twisted.internet import reactor, protocol
from twisted.internet.defer import DeferredQueue

HOST_NAME = "student02.cse.nd.edu" # this is the host that home will ssh to
HOST_PORT = 40017



# game connection
class GameConn(protocol.Protocol): #simply reiterate what they said.
	
	def connectionMade(self):
		self.transport.write("Beginning Player Connection...")
		self.queue = DeferredQueue()
	
	def dataReceived(self, data):
		#"As soon as any data is received, print it."
		print data
		self.queue.put(data)
		self.queue.get().addCallback(self.send_to_server)
		
	def send_to_server(self, data):
		self.transport.write(data)
			
	def connectionLost(self, reason):
		pass

class GameConnFactory(protocol.ClientFactory):
	def buildProtocol(self,addr):
		return GameConn()
	
	def clientConnectionFailed(self, connector, reason):
		print 'game server connection failed:', reason.getErrorMessage()
		reactor.stop()
	
	def clientConnectionLost(self, connector, reason):
		print 'game server connection lost:', reason.getErrorMessage()
		reactor.stop()


if __name__ == '__main__':
	
	#initiate game server connection!
	reactor.connectTCP(HOST_NAME, HOST_PORT, GameConnFactory())
	
	#run loop
	reactor.run()
