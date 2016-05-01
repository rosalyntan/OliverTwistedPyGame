# Rosalyn Tan, Nancy McNamara

from modes import sesame, pirates, bball, otwist

import os
import sys
import math
import random
import cPickle as pickle
import zlib

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import pygame
from pygame.locals import *

SERVER_HOST = 'localhost'
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
		self.player2 = Player2(self)

		self.bg = pygame.image.load("media/"+mode['background_image'])
		self.bg = pygame.transform.scale(self.bg, mode['background_scale'])
		#random variables in GameSpace
		self.score2 = 0
		self.keyspressed = 0

		self.quit = 0
		self.ready = 0

		#3. start game loop

	def game_loop(self):
		mx, my = pygame.mouse.get_pos()


		for bullet in self.player2.lasers:
			for guy in self.rain.drops:
				if collision(guy.rect.center, bullet.rect.center):
					self.rain.drops.remove(guy)
					self.player2.lasers.remove(bullet)
					self.score2+=1
					break

		#4. clock tick regulation (framerate)
		self.clock.tick(60)
		
		#5. handle user inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
		#		pygame.quit()
		#		sys.exit()
				self.quit = 1
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.player2.tofire = True
			if event.type == pygame.MOUSEBUTTONUP:
				self.player2.tofire = False

		#6. send a tick to every game object
		if self.ready == 1:
			self.rain.tick()
			self.player1.tick()
			self.player2.tick()
			for laser in self.player2.lasers:
				laser.tick()
#					self.player2.lasers.remove(laser)
			#7. finally, display game object
			self.screen.blit(self.bg, (0,0))
			self.screen.blit(self.player1.image, self.player1.rect)
			for laser in self.player2.lasers:
				self.screen.blit(laser.image, laser.rect)
			self.screen.blit(self.player2.image, self.player2.rect)
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render(str(self.score2), True, (100, 100, 100))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			self.screen.blit(self.player1.box.image, self.player1.box.rect)	
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			pygame.display.flip()
		else:
			self.screen.fill((0, 0, 0))
			lt = pygame.font.Font('freesansbold.ttf', 115)
			textSurf = lt.render("BUTTONS", True, (5, 100, 5))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			pygame.display.flip()	

class Rain(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.addNew = False
		self.drops = []
	def tick(self):
		if self.addNew:
			#print "HELLO\n\n\n\n\n", self.addNew
			self.drops.append(Raindrops(self.addNew, self.gs))
		for guy in self.drops:
			guy.rect = guy.rect.move([0,1])

class Raindrops(pygame.sprite.Sprite):
	def __init__(self, x, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['ball_image'])
		self.rect = self.image.get_rect()
		self.rect.center = [x,-25]

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
		pass
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

class Player2(pygame.sprite.Sprite):

	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.realx = 1
		self.realy = 1
		self.gs = gs
		self.image = pygame.image.load("media/canon2.jpg")
		self.rect = self.image.get_rect()
		self.rect.center = (600, 205)
		self.lasers = []
		#keep original image to limit resize errors
		self.orig_image = self.image

		#if I can fire laser beams, this flag will say whether I should be firing them right now
		self.tofire = False

	def tick(self):
		#get the mouse x and y position on the screen
		mx, my = pygame.mouse.get_pos()

		for guy in self.lasers:
			if guy.rect.center[0] < -20 or guy.rect.center[0] > 660:
				self.lasers.remove(guy)	
			elif guy.rect.center[1] < -20 or guy.rect.center[1] > 500:
				self.lasers.remove(guy)
		#this conditional prevents movement while firing
		if self.tofire == True:
			self.realx=mx
			self.realy=my
	
			#code to emit a laser beam block
			xSlope = self.realx-self.rect.center[0]
			ySlope = self.realy-self.rect.center[1]
			total = math.fabs(xSlope)+math.fabs(ySlope)
			self.lasers.append(Laser(self,self.rect.center[0],self.rect.center[1],xSlope/total, ySlope/total))
			self.tofire = False
		else:	
			#code to calculate the angle between my current direction and the mouse position (see math.atan2)
			angle = math.atan2(my-self.rect.center[1],mx-self.rect.center[0])*-180/math.pi+211.5
			#self.image = rot_center(self.orig_image, angle)	
			self.image = pygame.transform.rotate(self.orig_image, angle)
			self.rect = self.image.get_rect(center = self.rect.center)
			self.tofire = False

class Laser(pygame.sprite.Sprite):
	def __init__(self, gs=None, xc=320, yc=240, xm=1, ym=1):
		pygame.sprite.Sprite.__init__(self)
		xc=xc+xm*32
		yc=yc+ym*32
		self.xm=xm*10
		self.ym=ym*10
		self.gs = gs
		self.image = pygame.image.load("media/cannonball.png")
		self.rect = self.image.get_rect()
		self.rect.center=[xc,yc]

	def tick(self):
		self.rect = self.rect.move([self.xm,self.ym])
	
		
def dist(x1, y1, x2, y2):
	return ((y2-y1)**2+(x2-x1)**2)**.5

def collision(ball_center, bullet_center):
	distance = dist(ball_center[0], ball_center[1], bullet_center[0], bullet_center[1]) 
	if distance<=50:
		return True
	else:
		return False

class ClientConnection(Protocol):
	def __init__(self, client):
		self.client = client
	def dataReceived(self, data):
		if data == 'player 1 ready':
			self.ready = 1
		else:
			data =  pickle.loads(data)
			self.client.player1.rect.center = data[0]
			self.client.player1.box.rect.center = data[1]
			self.client.rain.addNew = data[2]
		if self.client.quit == 1:
			self.transport.loseConnection()
	def connectionMade(self):
		self.transport.write('player 2 connected')
	def connectionLost(self, reason):
		print 'lost connection to ' + SERVER_HOST + ' port ' + str(SERVER_PORT)
		reactor.stop()

class ClientConnFactory(ClientFactory):
	def __init__(self, client):
		self.client = client
	def buildProtocol(self, addr):
		return ClientConnection(self.client)


if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory(gs))
	reactor.run()
	lc.stop()
