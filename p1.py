# Rosalyn Tan, Nancy McNamara

# client game window only opens after server game window closes
# issue possibly stemming from the loop within the game state--data doesn't get transfered over to client until after server game loop ends. however, main for the server is called the data is sent to the client so idk

from modes import sesame, otwist, bball, pirates

import os
import sys
import math
import random
import cPickle as pickle
import zlib
#import copy

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall
import pygame
from pygame.locals import *

SERVER_PORT = 40041

mode = pirates

class GameSpace:
	def __init__(self):
		#1. basic initialization
		pygame.init()

		self.size = self.width, self.height = 640, 480
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("ppprrrrooooojjjjeeeeccccttttt")

		#2. set up game objects
		self.clock = pygame.time.Clock()
		self.rain = Rain(self)
		self.player1 = Player1(self)

		self.bg = pygame.image.load("media/"+mode['background_image'])
		self.bg = pygame.transform.scale(self.bg, mode['background_scale'])
		#random variables in GameSpace
		self.score1 = 0
		self.keyspressed = 0
		self.connected = False
	def game_loop(self):

	#		mx, my = pygame.mouse.get_pos()


		for guy in self.rain.drops:
			if collision(guy.rect.center, [self.player1.rect.center[0]+mode['catcher_offset'][0], self.player1.rect.center[1]+mode['catcher_offset'][1]]):
				self.rain.drops.remove(guy)
				self.score1+=1
		#4. clock tick regulation (framerate)
		self.clock.tick(60)
			
		#5. handle user inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == KEYDOWN:
				if event.key == 275:
					self.player1.Moving = "R" 
				elif event.key == 276:
					self.player1.Moving = "L"
				self.keyspressed +=1
			if event.type == KEYUP:
				self.keyspressed -=1
				if self.keyspressed ==0:
					self.player1.Moving = "N"
		if self.connected:
			#6. send a tick to every game object
			self.rain.tick()
			self.player1.tick()
			self.write(pickle.dumps([self.player1.rect.center, self.player1.box.rect.center, int(self.rain.created), self.score1]))
			#7. finally, display game object
			self.screen.blit(self.bg, (0,0))
			self.screen.blit(self.player1.image, self.player1.rect)
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render(str(self.score1), True, (100, 100, 100))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			self.screen.blit(self.player1.box.image, self.player1.box.rect)	
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			pygame.display.flip()
		else:
			self.screen.fill((0,0,0))
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render("BUTTONS", True, (5, 100, 5))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			pygame.display.flip()
	def write(self,data):
		pass
class Rain(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.drops = []
		self.created = False
	def tick(self):
		create = random.randint(1,10)
		if create==8:
			self.created = Raindrops(self.gs)
			self.drops.append(self.created)
			self.created = self.created.x
		else:
			self.created = False
		for guy in self.drops:
			guy.rect = guy.rect.move([0,1])

class Raindrops(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['ball_image'])
		self.rect = self.image.get_rect()
		self.x = random.randint(30,610)
		self.rect.center = [self.x,-25]

class Player1(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['player_image'])
		self.rect = self.image.get_rect()
		self.rect.center = mode['player_start']
		self.Moving = "N"
		self.box = Box(self.rect.center, self.gs)
	def tick(self):
		if self.Moving == "R":
			self.rect = self.rect.move([5,0])
			self.box.rect = self.box.rect.move([5,0])	
		elif self.Moving == "L":
			self.rect = self.rect.move([-5,0])
			self.box.rect = self.box.rect.move([-5,0])
		if self.rect.center[0]<mode['max_player_left']:
			self.rect.center = [mode['max_player_left'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0]+mode['box_offset'][0], self.rect.center[1]+mode['box_offset'][1]]
		elif self.rect.center[0]>mode['max_player_right']:
			self.rect.center = [mode['max_player_right'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0]+mode['box_offset'][0], self.rect.center[1]+mode['box_offset'][1]]

class Box(pygame.sprite.Sprite):
	def __init__(self, center, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['box_image'])
		self.rect = self.image.get_rect()
		self.x = center[0]+mode['box_offset'][0]
		self.y = center[1]+mode['box_offset'][1]
		self.rect.center = [self.x,self.y]

def dist(x1, y1, x2, y2):
	return ((y2-y1)**2+(x2-x1)**2)**.5

def collision(ball_center, catcher_point):
	distance = dist(ball_center[0], ball_center[1], catcher_point[0], catcher_point[1]) 
	if distance<=25:
		return True
	else:
		return False

class ServerConnection(Protocol):
	def __init__(self, addr, client):
		self.addr = addr
		self.client = client
#		self.gs = GameSpace()
	def dataReceived(self, data):
		print 'received data: ' + data
		if data == 'player 2 connected':
			self.client.connected = True	
		print "connection made"

	def connectionLost(self, reason):
		print 'connection lost from ' + str(self.addr)
		reactor.stop()
	def write(self, data):
		self.transport.write(data)
class ServerConnFactory(Factory):
	def __init__(self, client):
		self.client = client

	def buildProtocol(self, addr):
		proto = ServerConnection(addr, self.client)
		self.client.write = proto.write
		return proto


if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
	lc.stop()
