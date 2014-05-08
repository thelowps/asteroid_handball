# Kelly D Gawne & David Lopes
# This program listens for connections from a client computer
#RUN ME FIRST!

from twisted.internet import reactor, protocol, endpoints, defer
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall
import twisted.internet.error

import sys
import json

import game_engine

HOST_PORT = 40017 #port to listen on for connections
num_players = 0

playerConnections = {}
gs = None

class GameConn(protocol.Protocol): #respond to data received
    def connectionMade(self):
        global num_players
        num_players+=1
        playerConnections[str(num_players)] = self
        self.queue = DeferredQueue()
        #self.transport.write("Connected to server as player " + str(num_players))
        print self.queue
        
    def connectionLost(self, reason):
        pass
        
    def dataReceived(self, data):
        print data
        cucumber = json.loads(data)
        print cucumber
#       print data
#       self.queue.put(data)
#       self.queue.get().addCallback(self.send_to_client)
        
    def send_to_client(self, data):
        self.transport.write(data)
        
class GameConnFactory(protocol.ServerFactory):
    def buildProtocol(self,addr):
        return GameConn()
        
def server_loop ():
    if '1' in playerConnections and '2' in playerConnections:
        gs.game_loop()
        send_all( json.dumps(gs.get_game_description()) )
    else:
        print 'waiting for clients.'
    #if '1' in playerConnections.keys():
        #playerConnections['1'].queue.put("I'm loopy :op")
        #playerConnections['1'].queue.get().addCallback(playerConnections['1'].send_to_client)
        
def send_all(data):
    print "sending data: " + str(data)
    for p in playerConnections:
        conn = playerConnections[p]
        conn.transport.write(data)
        #conn.queue.put(data)
        #conn.queue.get().addCallback(conn.send_to_client)
    
def listenFailed(failure):
    print failure.getErrorMessage()
    #sys.exit(1)
    reactor.stop()

if __name__ == '__main__':
    
        #listen on CMD_PORT for commands from players:
    endpoint = endpoints.TCP4ServerEndpoint(reactor, HOST_PORT)
    d = endpoint.listen(GameConnFactory())
    d.addErrback(listenFailed)

    
    print "Listening for players on Port " + str(HOST_PORT) + "..."
    
    global gs
    gs = game_engine.GameSpace()
    gs.setup(server=True)
    
    #Loop
    tick = LoopingCall(server_loop)
    tick.start(1/30) #once a second
    #tick.stop will end the looping call
    
    reactor.run()
