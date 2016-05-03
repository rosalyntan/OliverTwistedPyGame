# Rosalyn Tan, Nancy McNamara

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

mode = otwist

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
		self.p2body = Player2Prop(self)

		#these lines set up the background image, could be done later and could be done in a function
		self.bg = pygame.image.load("media/"+mode['background_image'])
		self.bg = pygame.transform.scale(self.bg, mode['background_scale'])
		#random variables in GameSpace
		self.score1 = 0
		self.keyspressed = 0 #used to prevent player stopping if 2 keys are down at the same time and one is released
		self.connected = False #determines whether p2 has connected and game can start
		self.acked = False
		self.quit = 0
	def game_loop(self):

		for bullet in self.player2.lasers:
			for guy in self.rain.drops:
				if collision(guy.rect.center, bullet.rect.center):
					self.rain.drops.remove(guy)
					self.player2.lasers.remove(bullet)
					break

	#	mx, my = pygame.mouse.get_pos()

		#check for collisons between player box and coins, removes coins and increments score
		for guy in self.rain.drops:
			if collision(guy.rect.center, [self.player1.rect.center[0]+mode['catcher_offset'][0], self.player1.rect.center[1]+mode['catcher_offset'][1]]):
				self.rain.drops.remove(guy)
				self.score1+=1

		#4. clock tick regulation (framerate)
		self.clock.tick(60)
			
		#5. handle user inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
#				pygame.quit()
#				sys.exit()
				self.quit = 1
			if event.type == KEYDOWN:
				if event.key == 275: #right arrow
					self.player1.Moving = "R" 
				elif event.key == 276: #left arrow
					self.player1.Moving = "L"
				self.keyspressed +=1 
			if event.type == KEYUP:
				self.keyspressed -=1
				if self.keyspressed ==0:
					self.player1.Moving = "N"
		if self.connected: #p2 has connected to p1

			#6. send a tick to every game object
			self.rain.tick()
			self.player1.tick()
			self.player2.tick()
			for laser in self.player2.lasers:
				laser.tick()
			if self.acked:
				self.write(pickle.dumps([self.player1.rect.center, self.player1.box.rect.center, int(self.rain.created), self.score1])) #after ticks sent to objects, send location of player & box, send x value of new coin, send player 1 score
			self.acked = True
			#7. finally, display game object
			#background image
			self.screen.blit(self.bg, (0,0))

			self.screen.blit(self.p2body.image, self.p2body.rect)
			#player
			self.screen.blit(self.player1.image, self.player1.rect)
			for laser in self.player2.lasers:
#				print 'blit laser'
				self.screen.blit(laser.image, laser.rect)
			self.screen.blit(self.player2.image, self.player2.rect)
			#text & text display, could be done in a function
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render(str(self.score1), True, (100, 100, 100))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			#player box
			self.screen.blit(self.player1.box.image, self.player1.box.rect)
			#coins/balls/whatever
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			pygame.display.flip()
		else: #if p2 has not connected yet
			self.screen.blit(self.bg, (0, 0))
#			self.screen.fill((0,0,0))
			lt = pygame.font.Font('freesansbold.ttf',30)
			textSurf = lt.render("Waiting for p2 to connect...", True, (5, 100, 5))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			pygame.display.flip()
	def write(self,data): #dummy function so that we can use parent connection's write function
		pass
class Rain(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.drops = []
		self.created = False
	def tick(self): #create new falling item ~10% of the time
		create = random.randint(1,400)
		if create==8:
			self.created = Raindrops(self.gs)
			self.drops.append(self.created)
			self.created = self.created.x #sent to p2
		else:
			self.created = False #sent to p2
		for guy in self.drops:
			guy.rect = guy.rect.move([0,1]) #all coins down 1 pixel

class Raindrops(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['ball_image'])
		self.rect = self.image.get_rect()
		self.x = random.randint(30,610) #random x position for item
		self.rect.center = [self.x,-25] #starts above window

class Player2Prop(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['shooter_body'])
		self.rect = self.image.get_rect()
		self.rect.center = mode['sb_location']

class Player1(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['player_image'])
		self.rect = self.image.get_rect()
		self.rect.center = mode['player_start']
		self.Moving = "N"
		self.box = Box(self.rect.center, self.gs) #player's catching receptacle
	def tick(self):
		if self.Moving == "R":
			self.rect = self.rect.move([5,0])
			self.box.rect = self.box.rect.move([5,0])	
		elif self.Moving == "L":
			self.rect = self.rect.move([-5,0])
			self.box.rect = self.box.rect.move([-5,0])
		if self.rect.center[0]<mode['max_player_left']: #can't move left anymore, put player & box at maximum left position
			self.rect.center = [mode['max_player_left'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0]+mode['box_offset'][0], self.rect.center[1]+mode['box_offset'][1]]
		elif self.rect.center[0]>mode['max_player_right']: #same as above for right
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
#		self.realx = 1
#		self.realy = 1
		self.mx = 1
		self.my = 1
		self.gs = gs
		self.image = pygame.image.load("media/"+mode["gun_image"])
		self.rect = self.image.get_rect()
		self.rect.center = mode['gun_location']
		self.lasers = []
		self.angle = 0
		#keep original image to limit resize errors
		self.orig_image = self.image

		#if I can fire laser beams, this flag will say whether I should be firing them right now
		self.tofire = 0

	def tick(self):
		#get the mouse x and y position on the screen
#		mx, my = pygame.mouse.get_pos()

		for guy in self.lasers:
			if guy.rect.center[0] < -20 or guy.rect.center[0] > 660:
				self.lasers.remove(guy)	
			elif guy.rect.center[1] < -20 or guy.rect.center[1] > 500:
				self.lasers.remove(guy)
		#this conditional prevents movement while firing
		if self.tofire == 1:
#			self.realx=mx
#			self.realy=my
	
			#code to emit a laser beam block
#			print 'making lasers'
			xSlope = self.mx-self.rect.center[0]
			ySlope = self.my-self.rect.center[1]
			total = math.fabs(xSlope)+math.fabs(ySlope)
			self.lasers.append(Laser(self,self.rect.center[0],self.rect.center[1],xSlope/total, ySlope/total))
#			self.tofire = False
		else:	
			#code to calculate the angle between my current direction and the mouse position (see math.atan2)
			self.angle = math.atan2(self.my-self.rect.center[1],self.mx-self.rect.center[0])*-180/math.pi+211.5-mode['angle_offset']
			#self.image = rot_center(self.orig_image, angle)	
			self.image = pygame.transform.rotate(self.orig_image, self.angle)
			self.rect = self.image.get_rect(center = self.rect.center)
			self.tofire = 0

class Laser(pygame.sprite.Sprite):
	def __init__(self, gs=None, xc=320, yc=240, xm=1, ym=1):
		pygame.sprite.Sprite.__init__(self)
		xc=xc+xm*32
		yc=yc+ym*32
		self.xm=xm*10
		self.ym=ym*10
		self.gs = gs
		self.image = pygame.image.load("media/"+mode['bullet_image'])
		self.rect = self.image.get_rect()
		self.rect.center=[xc,yc]

	def tick(self):
		self.rect = self.rect.move([self.xm,self.ym])

#returns distance from one point to another
def dist(x1, y1, x2, y2):
	return ((y2-y1)**2+(x2-x1)**2)**.5

#returns whether two points are within 25 pixels of each other (radius of falling items)
def collision(ball_center, catcher_point):
	distance = dist(ball_center[0], ball_center[1], catcher_point[0], catcher_point[1]) 
	if distance<=25:
		return True
	else:
		return False

class ServerConnection(Protocol):
	def __init__(self, addr, client):
		self.addr = addr
		self.client = client #given a reference to GameSpace!
	def dataReceived(self, data):
#		print 'received data: ' + data
		if data == 'player 2 connected': #alerts GameSpace when p2 has connected
			self.client.connected = True
			self.transport.write('player 1 ready')
		else:
			data = pickle.loads(data)
#			print data[2]
			self.client.player2.mx = data[0]
			self.client.player2.my = data[1]
			self.client.player2.tofire = data[2]
#		print "connection made"
		if self.client.quit == 1:
			self.transport.loseConnection()
	def connectionLost(self, reason):
		print 'connection lost from ' + str(self.addr)
		reactor.stop()
	def write(self, data): #write function used in GameSpace
		self.transport.write(data)

class ServerConnFactory(Factory):
	def __init__(self, client):
		self.client = client #given reference to GameSpace
	def buildProtocol(self, addr):
		proto = ServerConnection(addr, self.client)
		self.client.write = proto.write #sets write function in GameSpace to connection's write function
		return proto


#I DON'T REALLY KNOW WHAT THIS DOES BUT IT WAS GIVEN IN CLASS???
if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
	lc.stop()
