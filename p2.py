# Rosalyn Tan, Nancy McNamara

#THIS IS PLAYER 2, THE MORE CLIENT-Y CLIENT, THE ONE WHO SHOOTS AT THINGS

from modes import backgrounds, sesame, pirates, bball, otwist

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
#		self.score2 = 0
		self.keyspressed = 0
		self.mode = None
		self.quit = 0
		self.ready = 0
		self.acked = 0
		tempMode = backgrounds[random.randint(0,3)]
		self.bg = pygame.image.load("media/"+tempMode['background_image'])
		self.bg = pygame.transform.scale(self.bg, tempMode['background_scale'])
		self.gameOver = 0

#		random.seed()

		#3. start game loop
	def setup(self):
		self.tickNum = 0
		self.score1 = 0
		self.score2 = 0
		self.rain = Rain(self)
		self.player1 = Player1(self)
		self.player2 = Player2(self)
		self.p2body = Player2Prop(self)
		self.endGame = GameOver(self)

		self.bg = pygame.image.load("media/"+self.mode['background_image'])
		self.bg = pygame.transform.scale(self.bg, self.mode['background_scale'])

	def game_loop(self):
		if self.gameOver == 1:
			self.endGame.display(2)
			pygame.display.flip()
		elif self.ready ==1:
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
					self.player2.tofire = 1
				if event.type == pygame.MOUSEBUTTONUP:
					self.player2.tofire = 0

		#6. send a tick to every game object
	#	if self.ready == 1:
			self.rain.tick()
			self.player1.tick()
			self.player2.tick()
			self.tickNum+=1
			for laser in self.player2.lasers:
				laser.tick()
			if self.acked == 1 and self.tickNum%20 == 0:
				laserListx = []
				laserListy = []
				for laser in self.player2.lasers:
					laserListx.append(laser.rect.centerx)
					laserListy.append(laser.rect.centery)
				# player 2 should send over rotation information, score, laser locations
				self.write(zlib.compress(pickle.dumps([self.player2.mx, self.player2.my, self.score2, pickle.dumps(laserListx), pickle.dumps(laserListy)])))
				self.player2.fired = 0 # might not need this
			self.acked = 1
			if self.score2 > 20:
				self.gameOver = 1
			#7. finally, display game object
			self.screen.blit(self.bg, (0,0))
			self.screen.blit(self.p2body.image, self.p2body.rect)
			self.screen.blit(self.player1.image, self.player1.rect)
			for laser in self.player2.lasers:
				self.screen.blit(laser.image, laser.rect)
			self.screen.blit(self.player2.image, self.player2.rect)
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render(str(self.score2), True, (100, 100, 100))
			TextRect = textSurf.get_rect()
			text2Surf = lt.render(str(self.score1), True, (100,100,100))
			TextRect2 = text2Surf.get_rect()
			TextRect2.center = [64,178]
#			print TextRect2.size	
			self.screen.blit(text2Surf, TextRect2)
			self.screen.blit(textSurf, TextRect)
			self.screen.blit(self.player1.box.image, self.player1.box.rect)	
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			pygame.display.flip()
		else:
			randback = random.randint(1,4)	
			self.screen.blit(self.bg, (0, 0))
#			self.screen.fill((0, 0, 0))
			lt = pygame.font.Font('freesansbold.ttf', 50)
			textSurf = lt.render("Waiting for Player 1", True, (5, 100, 5))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			pygame.display.flip()
	def write(self, data): # dummy function
		pass

class GameOver(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
		self.playAgain = pygame.image.load("media/penny.png") # need to change image
		self.quit = pygame.image.load("media/cookie.png") # need to change image
		self.playRect = self.playAgain.get_rect()
		self.quitRect = self.quit.get_rect()

		self.playRect.center = [175, 200]
		self.quitRect.center = [465, 200]
		self.messageSent = 0
	def display(self, winner):
		if self.messageSent == 0:
			self.gs.write('game over')
			print 'game over sent'
			self.messageSent = 1
		self.gs.screen.fill((0, 0, 0))
		if winner == 1:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			textSurf = lt.render("You lost :(", True, (255, 255, 255))
			textRect = textSurf.get_rect()
		elif winner == 2:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			textSurf = lt.render("You win! :)", True, (255, 255, 255))
			textRect = textSurf.get_rect()
		self.gs.screen.blit(textSurf, textRect)
		self.gs.screen.blit(self.playAgain, self.playRect)
		self.gs.screen.blit(self.quit, self.quitRect)
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				mx, my = pygame.mouse.get_pos()
				if mx > self.playRect.centerx-25 and mx < self.playRect.centerx+25 and my > self.playRect.centery-25 and my < self.playRect.centery+25:
#					self.gs.write('player 2 connected')
					self.gs.gameOver = 0
					self.gs.ready = 0
					self.gs.acked = 0
					self.messageSent = 0
					self.gs.write('player 2 connected')
					print 'clicked play again'
				elif mx > self.quitRect.centerx-25 and mx < self.quitRect.centerx+25 and my > self.quitRect.centery-25 and my < self.quitRect.centery+25:
					print 'clicked quit'
					self.gs.quit = 1

class Rain(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.addNew = False
		self.drops = []
	def tick(self):
#		if self.addNew:
#			self.drops.append(Raindrops(self.addNew, -25, self.gs))
		for guy in self.drops:
			guy.rect = guy.rect.move([0,1])

class Raindrops(pygame.sprite.Sprite):
	def __init__(self, x, y, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['ball_image'])
		self.rect = self.image.get_rect()
		self.rect.center = [x,y]

class Player2Prop(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['shooter_body'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['sb_location']

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
		if self.Moving == "R":
			self.rect = self.rect.move([5,0])
			self.box.rect = self.box.rect.move([5,0])	
		elif self.Moving == "L":
			self.rect = self.rect.move([-5,0])
			self.box.rect = self.box.rect.move([-5,0])
		if self.rect.center[0]<self.gs.mode['max_player_left']:
			self.rect.center = [self.gs.mode['max_player_left'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0]+self.gs.mode['box_offset'][0], self.rect.center[1]+self.gs.mode['box_offset'][1]]
		elif self.rect.center[0]>self.gs.mode['max_player_right']:
			self.rect.center = [self.gs.mode['max_player_right'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0]+self.gs.mode['box_offset'][0], self.rect.center[1]+self.gs.mode['box_offset'][1]]

class Box(pygame.sprite.Sprite):
	def __init__(self, center, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['box_image'])
		self.rect = self.image.get_rect()
		self.x = center[0]+self.gs.mode['box_offset'][0]
		self.y = center[1]+self.gs.mode['box_offset'][1]
		self.rect.center = [self.x,self.y]

class Player2(pygame.sprite.Sprite):

	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.realx = 1
		self.realy = 1
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode["gun_image"])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['gun_location']
#		self.rect.center = (600, 205)
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
			self.lasers.append(Laser(self.rect.center[0], self.rect.center[1], xSlope/total, ySlope/total, self.gs))
#			self.lasers.append(Laser(self,startx,starty,xSlope/total, ySlope/total))
			self.tofire = 0
			self.fired = 1
		else:	
			#code to calculate the angle between my current direction and the mouse position (see math.atan2)
			self.angle = math.atan2(self.my-self.rect.center[1],self.mx-self.rect.center[0])*-180/math.pi+211.5#-self.gs.mode['angle_offset']
			#self.image = rot_center(self.orig_image, angle)	
			self.image = pygame.transform.rotate(self.orig_image, self.angle)
			self.rect = self.image.get_rect(center = self.rect.center)
			self.tofire = 0

class Laser(pygame.sprite.Sprite):
	def __init__(self, xc=320, yc=240, xm=1, ym=1, gs=None):
		pygame.sprite.Sprite.__init__(self)
		xc=xc+xm*125
		yc=yc+ym*125
		self.xm=xm*10
		self.ym=ym*10
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['bullet_image'])
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
		self.queue = DeferredQueue()
	def dataReceived(self, data):
#		data = data # sometimes it works better with this line?????
		if self.client.quit == 1:
			print 'quit called'
			self.transport.loseConnection()
		if data == 'sesame':
			print 'sesame'
			self.client.mode = sesame
#			print 'string' + data
			self.client.setup()
			self.client.ready = 1
		elif data=='pirates':
			print 'pirates'
			self.client.mode=pirates
			self.client.setup()
			self.client.ready = 1
		elif data == 'bball':
			print 'bball'
			self.client.mode = bball
			self.client.setup()
			self.client.ready = 1
		elif data == 'otwist':
			print 'otwist'
			self.client.mode = otwist
			self.client.setup()
			self.client.ready = 1
		else:
			data =  pickle.loads(zlib.decompress(data))
			self.client.player1.rect.center = data[0]
			self.client.player1.box.rect.center = data[1]
			self.client.score1 = data[2]
			self.client.rain.drops = []
			rainx = pickle.loads(data[3])
			rainy = pickle.loads(data[4])
			i=0
			for x in rainx:
				self.client.rain.drops(append(Raindrop(x, rainy[i], self.client)))
				i+=1
#			print pickle.loads(data[3])
#			print pickle.loads(data[4])
	def connectionMade(self):
		self.transport.write('player 2 connected')
	def connectionLost(self, reason):
		print 'lost connection to ' + SERVER_HOST + ' port ' + str(SERVER_PORT)
		reactor.stop()
	def write(self, data):
		self.transport.write(data)

class ClientConnFactory(ClientFactory):
	def __init__(self, client):
		self.client = client
	def buildProtocol(self, addr):
		proto = ClientConnection(self.client)
		self.client.write = proto.write # sets write function in GameSpace to connection's write function
		return proto


if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory(gs))
	reactor.run()
	lc.stop()
