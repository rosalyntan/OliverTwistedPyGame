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

pirates = dict([
	("player_image","pirate.png"),
	("background_image","piratebeach.jpg"),
	("box_image", "treasurechest.png"), 
	("ball_image", "piratecoin.png"), 
	('gun_image', "canon2.jpg"), 
	('player_start', [300,400]),
	('max_player_left',20),
	('max_player_right',620),
	('box_offset',[-15,38]),
	('background_scale',[854,480]),
	('catcher_offset',[-10,40])
])

bball = dict([
	("player_image","kobe.png"),
	("background_image","lakerscourt.png"),
	("box_image", "hoop.png"), 
	("ball_image", "basketball.png"), 
	('gun_image', "canon2.jpg"), 
	('player_start', [300,400]),
	('max_player_left',20),
	('max_player_right',475),
	('box_offset',[140,40]),
	('background_scale',[854,480]),
	('catcher_offset',[140,0])
])

mode = bball

class ServerConnection(Protocol):
	def __init__(self, addr):
		self.addr = addr
		self.gs = GameSpace()
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

class GameSpace:
	def main(self):
		#1. basic initialization
		pygame.init()

		self.size = self.width, self.height = 640, 480
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("ppprrrrooooojjjjeeeeccccttttt")

		#2. set up game objects
		self.clock = pygame.time.Clock()
		self.rain = Rain(self)
		self.player1 = Player1(self)

		bg = pygame.image.load("media/"+mode['background_image'])
		bg = pygame.transform.scale(bg, mode['background_scale'])
		#random variables in GameSpace
		self.score1 = 0
		self.keyspressed = 0

		#3. start game loop
		while 1:
			mx, my = pygame.mouse.get_pos()


			for guy in self.rain.drops:
				if collision(guy.rect.center, [self.player1.rect.center[0]+mode['catcher_offset'][0], self.player1.rect.center[1]+mode['catcher_offset'][1]]):
					self.rain.drops.remove(guy)
					self.score1+=1
					print self.player1.rect.center
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
			#6. send a tick to every game object
			self.rain.tick()
			self.player1.tick()

reactor.listenTCP(SERVER_PORT, ServerConnFactory())
#lc = LoopingCall(game_loop_iterate)
#lc.start(1/60)
reactor.run()
#lc.stop()
