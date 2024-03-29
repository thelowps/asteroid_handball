# Kelly D Gawne & David Lopes
# This program listens for connections from a client computer
#RUN ME FIRST!

from twisted.internet import reactor, protocol, endpoints, defer
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall
import twisted.internet.error
import sys

import game_engine

HOST_PORT = 40017 #port to listen on for connections
num_players = 0

class GameConn(protocol.Protocol): #respond to data received
    def connectionMade(self):
        global num_players
        num_players+=1
        playerConnections[str(num_players)] = self
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
        
def runME():
    if '1' in playerConnections.keys():
        self.queue.put("I'm loopy :op")
        self.queue.get().addCallback(self.send_to_client)
        
def send_all(data):
    for playerConn in playerConnections:
        playerConn.queue.put("Howdy, y'all (<:|D")
        playerConn.queue.get().addCallback(self.send_to_client)
    
def listenFailed(failure):
    print failure.getErrorMessage()
    #sys.exit(1)
    reactor.stop()


if __name__ == '__main__':
    playerConnections = {}
    
    #listen on CMD_PORT for commands from players:
    endpoint = endpoints.TCP4ServerEndpoint(reactor, HOST_PORT)
    d = endpoint.listen(GameConnFactory())
    d.addErrback(listenFailed)

    
    print "Listening for players on Port " + str(HOST_PORT) + "..."

    # Start game loop
    gs = game_engine.GameSpace()
    gs.setup()
    
    #Loop
    tick = LoopingCall(gs.game_loop)
    tick.start(1/30) #once a second
    #tick.stop will end the looping call
    
    reactor.run()
