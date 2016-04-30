# Rosalyn Tan, Nancy McNamara

import os
import sys
import math
import random

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor

import pygame
from pygame.locals import *

SERVER_HOST = 'student01.cse.nd.edu'
SERVER_PORT = 40041

class ClientConnection(Protocol):
	def dataReceived(self, data):
		print 'received data: ' + data
	def connectionMade(self):
		self.transport.write('player 2 connected')
	def connectionLost(self, reason):
		print 'lost connection to ' + SERVER_HOST + ' port ' + str(SERVER_PORT)
		reactor.stop()

class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return ClientConnection()

reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory())
reactor.run()
