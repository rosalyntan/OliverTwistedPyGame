# Rosalyn Tan, Nancy McNamara

#THIS IS PLAYER 2, THE MORE CLIENT-Y CLIENT, THE ONE WHO SHOOTS AT THINGS

from modes import backgrounds, sesame, pirates, bball, otwist # four different modes to choose from--customizable gameplay

import os
import sys
import math
import random
import cPickle as pickle
import zlib

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

import pygame
from pygame.locals import *

SERVER_HOST = 'localhost'
SERVER_PORT = 40041

class GameSpace:
	def __init__(self):
		#1. basic initialization
		pygame.init()

		self.size = self.width, self.height = 640, 480
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("Oliver Twisted Pygame")

		#2. set up game objects
		self.clock = pygame.time.Clock()

		#random variables in GameSpace
		self.keyspressed = 0
		self.mode = None
		self.quit = 0
		self.ready = 0
		self.acked = 0
		# initial random background for waiting screen
		tempMode = backgrounds[random.randint(0,3)]
		self.bg = pygame.image.load("media/"+tempMode['background_image'])
		self.bg = pygame.transform.scale(self.bg, tempMode['background_scale'])
		self.gameOver = 0
	def setup(self):
		self.tickNum = 0
		self.score1 = 0
		self.score2 = 0
		# initialize game objects
		self.rain = Rain(self)
		self.player1 = Player1(self)
		self.player2 = Player2(self)
		self.p2body = Player2Prop(self)
		self.endGame = GameOver(self)
		# load background image
		self.bg = pygame.image.load("media/"+self.mode['background_image'])
		self.bg = pygame.transform.scale(self.bg, self.mode['background_scale'])
	#3. start game loop
	def game_loop(self):
		# when the game ends
		if self.gameOver == 1:
			if self.score1 > 20:
				self.endGame.display(1)
			else:
				self.endGame.display(2)
			pygame.display.flip()
		elif self.ready ==1:
			#4. clock tick regulation (framerate)
			self.clock.tick(60)
			
			#5. handle user inputs
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					self.player2.tofire = 1
				if event.type == pygame.MOUSEBUTTONUP:
					self.player2.tofire = 0

		#6. send a tick to every game object
			self.rain.tick()
			self.player1.tick()
			self.player2.tick()
			self.tickNum+=1
			for laser in self.player2.lasers:
				laser.tick()
			# send information to player 1 every three ticks
			if self.acked == 1 and self.tickNum%3 == 0:
				laserListx = []
				laserListy = []
				laserListxm = []
				laserListym = []
				# list of all laser x, y coordinates, as well as slopes
				for laser in self.player2.lasers:
					laserListx.append(laser.rect.centerx)
					laserListy.append(laser.rect.centery)
					laserListxm.append(laser.xm)
					laserListym.append(laser.ym)
				# player 2 sends over rotation information, score, laser locations, laser slopes
				self.write(zlib.compress(pickle.dumps([self.player2.mx, self.player2.my, pickle.dumps(laserListx), pickle.dumps(laserListy), pickle.dumps(laserListxm), pickle.dumps(laserListym)])))
			self.acked = 1
			#7. finally, display game object
			self.screen.blit(self.bg, (0,0))
			self.screen.blit(self.p2body.image, self.p2body.rect)
			self.screen.blit(self.player1.image, self.player1.rect)
			# blit lasers
			for laser in self.player2.lasers:
				self.screen.blit(laser.image, laser.rect)
			self.screen.blit(self.player2.image, self.player2.rect)
			#text & text display, could be done in a function
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render(str(self.score1), True, (255, 0, 169))
			TextRect = textSurf.get_rect()
			text2Surf = lt.render(str(self.score2), True, (255,255,255))
			TextRect2 = text2Surf.get_rect()
			if self.score2>self.score1:
				TextRect.center = [TextRect.size[1]/2, 150]
				TextRect2.center = [TextRect2.size[1]/2,50]
			else:
				TextRect.center = [TextRect.size[1]/2, 50]
				TextRect2.center = [TextRect2.size[1]/2,150]
			self.screen.blit(text2Surf, TextRect2)
			self.screen.blit(textSurf, TextRect)
			self.screen.blit(self.player1.box.image, self.player1.box.rect)
			# blit falling sky stuff
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			pygame.display.flip()
			# end-game condition
			if self.score2 > 20 or self.score1 > 20:
				self.gameOver = 1
		else:
			randback = random.randint(1,4)	
			self.screen.blit(self.bg, (0, 0))
			lt = pygame.font.Font('freesansbold.ttf', 50)
			textSurf = lt.render("Waiting for Player 1", True, (255, 255, 255))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			pygame.display.flip()
	def write(self, data): # dummy function
		pass
	def quit(self): # dummy function
		pass

class GameOver(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
	def display(self, winner):
		self.gs.screen.fill((0, 0, 0))
		# player 1 wins
		if winner == 1:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			textSurf = lt.render("You lost :(", True, (255, 255, 255))
		# player 2 wins
		elif winner == 2:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			textSurf = lt.render("You win! :)", True, (255, 255, 255))
		textRect = textSurf.get_rect()
		textRect.center = [200, 300]
		self.gs.screen.blit(textSurf, textRect)
		# quit from game over screen
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.gs.quit()

# holds list of Raindrops objects, the stuff that falls from the sky
class Rain(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.addNew = False
		self.drops = []
	def tick(self):
		# make the raindrops fall down
		for guy in self.drops:
			guy.rect = guy.rect.move([0,1])

# each individual sky thing
class Raindrops(pygame.sprite.Sprite):
	def __init__(self, x, y, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['ball_image'])
		self.rect = self.image.get_rect()
		self.rect.center = [x,y]

# static player 2 character on the right side of the screen (only the arm moves, in a different class)
class Player2Prop(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['shooter_body'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['sb_location']

# player 1 object--location info comes from player 1
class Player1(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['player_image'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['player_start']
		self.Moving = "N"
		self.box = Box(self.rect.center, self.gs)
	def tick(self):
		pass

# player 1 catches things in here
class Box(pygame.sprite.Sprite):
	def __init__(self, center, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['box_image'])
		self.rect = self.image.get_rect()
		self.x = center[0]+self.gs.mode['box_offset'][0]
		self.y = center[1]+self.gs.mode['box_offset'][1]
		self.rect.center = [self.x,self.y]

# player 2 (the person running this file)
class Player2(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.realx = 1
		self.realy = 1
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode["gun_image"])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['gun_location']
		self.lasers = []
		self.angle = 0
		#keep original image to limit resize errors
		self.orig_image = self.image

		#if I can fire laser beams, this flag will say whether I should be firing them right now
		self.tofire = 0
		self.fired = 0
	def tick(self):
		#get the mouse x and y position on the screen
		self.mx, self.my = pygame.mouse.get_pos()
		# remove lasers when they go off-screen
		for guy in self.lasers:
			if guy.rect.center[0] < -20 or guy.rect.center[0] > 660:
				self.lasers.remove(guy)	
			elif guy.rect.center[1] < -20 or guy.rect.center[1] > 500:
				self.lasers.remove(guy)
		#this conditional prevents movement while firing
		if self.tofire == 1:
			self.realx=self.mx
			self.realy=self.my
	
			#code to emit a laser beam block
			xSlope = self.realx-self.rect.center[0]
			ySlope = self.realy-self.rect.center[1]
				
			total = math.fabs(xSlope)+math.fabs(ySlope)
			# only allow one laser on the screen at a time--could change to be more to make it harder for player 1
			if len(self.lasers) < 1:
				self.lasers.append(Laser(self.rect.center[0], self.rect.center[1], xSlope/total, ySlope/total, self.gs))
			self.tofire = 0
			self.fired = 1
		else:	
			#code to calculate the angle between my current direction and the mouse position (see math.atan2)
			self.angle = math.atan2(self.my-self.rect.center[1],self.mx-self.rect.center[0])*-180/math.pi+211.5-self.gs.mode['angle_offset']
			# rotate shooting arm
			self.image = pygame.transform.rotate(self.orig_image, self.angle)
			self.rect = self.image.get_rect(center = self.rect.center)
			self.tofire = 0

# the things flying across the screen from player 2
class Laser(pygame.sprite.Sprite):
	def __init__(self, xc=320, yc=240, xm=1, ym=1, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		xc=xc+xm*self.gs.mode['bullet_offset']
		yc=yc+ym*self.gs.mode['bullet_offset']
		self.xm=xm*10
		self.ym=ym*10
		self.image = pygame.image.load("media/"+self.gs.mode['bullet_image'])
		self.rect = self.image.get_rect()
		self.rect.center=[xc,yc]
	def tick(self):
		# move lasers across the screen at angle they were shot at
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
		# detect which mode is chosen
		if data == 'sesame':
			self.client.mode = sesame
			self.client.setup()
			self.client.ready = 1
		elif data=='pirates':
			self.client.mode=pirates
			self.client.setup()
			self.client.ready = 1
		elif data == 'bball':
			self.client.mode = bball
			self.client.setup()
			self.client.ready = 1
		elif data == 'otwist':
			self.client.mode = otwist
			self.client.setup()
			self.client.ready = 1
		# pickled data is sent from player 1
		else:
			data =  pickle.loads(zlib.decompress(data))
			# player 1 location
			self.client.player1.rect.center = data[0]
			self.client.player1.box.rect.center = data[1]
			# player 1 score
			self.client.score1 = data[2]
			# rain drop locations
			self.client.rain.drops = []
			rainx = pickle.loads(data[3])
			rainy = pickle.loads(data[4])
			i=0
			for x in rainx:
				self.client.rain.drops.append(Raindrops(x, rainy[i], self.client))
				i+=1
			# player 2 score
			self.client.score2=data[5]
	def connectionMade(self):
		self.transport.write('player 2 connected')
	def connectionLost(self, reason):
		reactor.stop()
	def write(self, data): # connects to game space function
		self.transport.write(data)
	def quit(self): # connects to game space function
		self.transport.loseConnection()

class ClientConnFactory(ClientFactory):
	def __init__(self, client):
		self.client = client
	def buildProtocol(self, addr):
		proto = ClientConnection(self.client)
		self.client.write = proto.write # sets write function in GameSpace to connection's write function
		self.client.quit = proto.quit # sets quit function in GameSpace to connection's quit function
		return proto

# starts game loop
if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory(gs))
	reactor.run()
	lc.stop()
