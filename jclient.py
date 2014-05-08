#Kelly D Gawne & David Lopes
#	Connects to server and draws shit

from twisted.internet import reactor, protocol
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

import game_engine

HOST_NAME = "student02.cse.nd.edu" # this is the host that home will ssh to
HOST_PORT = 40017
FRAME_RATE = 1/30.0


# game connection
class GameConn(protocol.Protocol): #simply reiterate what they said.
	def connectionMade(self):
		#self.transport.write("Beginning Player Connection...")
		self.queue = DeferredQueue()
        self.queue.get().addCallback(self.receivedJSON)
		self.transport.write(json.dumps({"bob":"saggett", "nick": "cage"}, encoding='latin-1'))
		
	def dataReceived(self, data):
        self.queue.put(data)
        self.queue.get().addCallback(self.receivedJSON)
		
    def receivedJSON(self, data):
        content = json.loads(data)
        print content

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
		#reactor.stop()
		
def tick_all():
	#tick player
	#pass resulting rect to server.	
	pass


if __name__ == '__main__':
	
	#initiate game server connection!
	reactor.connectTCP(HOST_NAME, HOST_PORT, GameConnFactory())
	
#	cucumber = {"bob":"saggett", "nick": "cage"}
#	yum = json.dumps(cucumber, encoding='latin-1')
#	print yum
#	#gross = pickle.load(open("cucumber.p","rb"))
#	gross = json.loads(yum)
#	print gross
	
	#Loop
	tick = LoopingCall(tick_all)
	tick.start(FRAME_RATE) #once a second
	#tick.stop will end the looping call
	
	reactor.run()
