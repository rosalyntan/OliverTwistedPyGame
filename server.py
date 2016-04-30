# Rosalyn Tan, Nancy McNamara

import os
import sys
import math
import random

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor

import pygame
from pygame.locals import *

SERVER_PORT = 40041

class ServerConnection(Protocol):
	def __init__(self, addr):
		self.addr = addr
		self.gs
	def dataReceived(self, data):
		print 'received data: ' + data
	def connectionMade(self):
		self.transport.write('player 1 connected')
	def connectionLost(self, reason):
		print 'connection lost from ' + str(self.addr)
		reactor.stop()

class ServerConnFactory(Factory):
	def buildProtocol(self, addr):
		return ServerConnection(addr)

reactor.listenTCP(SERVER_PORT, ServerConnFactory())
lc = LoopingCall(game_loop_iterate)
lc.start(1/60)
reactor.run()
lc.stop()
