# Rosalyn Tan, Nancy McNamara

#THIS IS PLAYER 1, THE SUPERCLIENT, THE ONE WHO CATCHES THINGS

from modes import sesame, otwist, bball, pirates # customizable game play, four different modes to choose from

import os
import sys
import math
import random
import cPickle as pickle
import zlib

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

import pygame
from pygame.locals import *

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
		self.menu = Menu(self)

		#random variables in GameSpace
		self.counter = 0
		self.keyspressed = 0 #used to prevent player stopping if 2 keys are down at the same time and one is released
		self.connected = False #determines whether p2 has connected and game can start
		self.acked = False
		self.quit = 0
		self.mode = None
		self.waitingString = "Waiting for p2 to connect..."
		self.gameOver = 0
	def setup(self):
		self.score1 = 0
		self.score2 = 0
		self.scoreCount = 0
		# initialize game objects
		self.rain = Rain(self)
		self.player1 = Player1(self)
		self.player2 = Player2(self)
		self.p2body = Player2Prop(self)
		self.endGame = GameOver(self)
		# load background image
		self.bg = pygame.image.load("media/"+self.mode['background_image'])
		self.bg = pygame.transform.scale(self.bg, self.mode['background_scale'])
	def game_loop(self):
		if self.gameOver == 1:
			self.write(zlib.compress(pickle.dumps([self.player1.rect.center, self.player1.box.rect.center, self.score1, pickle.dumps([]), pickle.dumps([]), self.score2]))) # updates player 2 score when player 1 wins/loses so player 2 can also end the game
			if self.score1 > 20:
				self.endGame.display(1)
			else:
				self.endGame.display(2)
			pygame.display.flip()
		elif self.connected and self.mode != None: # player 2 is connected and player 1 has chosen a mode
			self.counter+=1;
			#collision detection code
			for bullet in self.player2.lasers:
				for guy in self.rain.drops:
					if collision(guy.rect.center, bullet.rect.center):
						self.rain.drops.remove(guy)
						self.player2.lasers.remove(bullet)
						if self.scoreCount%3 == 1: # player 2 gets a point for every 3 objects hit, in order to keep it fair
							self.score2+=1
						self.scoreCount+=1
						break
			#check for collisons between player box and coins, removes coins and increments score
			for guy in self.rain.drops:
				if collision(guy.rect.center, [self.player1.rect.center[0]+self.mode['catcher_offset'][0], self.player1.rect.center[1]+self.mode['catcher_offset'][1]]):
					self.rain.drops.remove(guy)
					self.score1+=1
			#4. clock tick regulation (framerate)
			self.clock.tick(60)
			#5. handle user inputs
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit()
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
		#6. send a tick to every game object
			self.rain.tick()
			self.player1.tick()
			self.player2.tick()
			for laser in self.player2.lasers:
				laser.tick()
			if self.acked and self.counter%3==0: # sends info to player 2 every three ticks
				rainx = []
				rainy = []
				# make list of rain drop x,y coordinates to send to player 2
				for drop in self.rain.drops:
					rainx.append(drop.rect.center[0])
					rainy.append(drop.rect.center[1])
			
				self.write(zlib.compress(pickle.dumps([self.player1.rect.center, self.player1.box.rect.center, self.score1, pickle.dumps(rainx), pickle.dumps(rainy), self.score2]))) #after ticks sent to objects, send location of player & box, player 1 score, rain coordinates, and player 2 score
			self.acked = True
			#7. finally, display game object
			#background image
			self.screen.blit(self.bg, (0,0))
			self.screen.blit(self.p2body.image, self.p2body.rect)
			#player
			self.screen.blit(self.player1.image, self.player1.rect)
			# lasers
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
			#player box
			self.screen.blit(self.player1.box.image, self.player1.box.rect)
			#coins/balls/whatever
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			pygame.display.flip()
			# end-game condition
			if self.score2 > 20 or self.score1 > 20:
				self.gameOver = 1
		else: #if p2 has not connected yet
			self.menu.display()
			pygame.display.flip()	
	def write(self,data): #dummy function so that we can use parent connection's write function
		pass
	def quit(self): # dummy function connected to connection's quit function
		pass

# menu screen to choose different modes
class Menu(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		# button images to choose different modes
		self.pirateButton = pygame.image.load("media/penny.png")
		self.bballButton = pygame.image.load("media/basketball.png")
		self.otwistButton = pygame.image.load("media/porridge.png")
		self.sesameButton = pygame.image.load("media/cookie.png")
		
		self.pirateRect = self.pirateButton.get_rect()
		self.bballRect = self.bballButton.get_rect()
		self.otwistRect = self.otwistButton.get_rect()
		self.sesameRect = self.sesameButton.get_rect()

		self.pirateRect.center = [145, 300]
		self.bballRect.center = [245, 300]
		self.otwistRect.center = [345, 300]
		self.sesameRect.center = [445, 300]
		
		self.circleCenter = None
	def display(self):
		mx, my = pygame.mouse.get_pos()

		self.gs.screen.fill((0, 0, 0))
		lt = pygame.font.Font('freesansbold.ttf', 80)
		textSurf = lt.render("Choose a mode!", True, (255, 255, 255))
		textRect = textSurf.get_rect()
		self.gs.screen.blit(textSurf, textRect)

		message = pygame.font.Font('freesansbold.ttf', 30)
		messSurf = message.render(self.gs.waitingString, True, (255, 255, 255))
		messRect = messSurf.get_rect()
		messRect.center = 450,460
		self.gs.screen.blit(messSurf, messRect)

		# highlight button when hovering over it
		if dist(mx,my,self.pirateRect.centerx,self.pirateRect.centery)<25:
			pygame.draw.circle(self.gs.screen, (255,0,169), [self.pirateRect.centerx,self.pirateRect.centery], 50,0)
		elif  dist(mx,my,self.bballRect.centerx,self.bballRect.centery)<25:
			pygame.draw.circle(self.gs.screen, (255,0,169), [self.bballRect.centerx,self.bballRect.centery], 50,0)
		elif dist(mx,my,self.otwistRect.centerx,self.otwistRect.centery)<25:
			pygame.draw.circle(self.gs.screen, (255,0,169), [self.otwistRect.centerx,self.otwistRect.centery], 50,0)
		elif dist(mx,my,self.sesameRect.centerx,self.sesameRect.centery)<25:
			pygame.draw.circle(self.gs.screen, (100,100,0), [self.sesameRect.centerx,self.sesameRect.centery], 50,0)
		elif self.circleCenter != None:
			pygame.draw.circle(self.gs.screen, (100,100,0), self.circleCenter, 50,0)

		# display buttons	
		self.gs.screen.blit(self.pirateButton, self.pirateRect)
		self.gs.screen.blit(self.bballButton, self.bballRect)
		self.gs.screen.blit(self.otwistButton, self.otwistRect)
		self.gs.screen.blit(self.sesameButton, self.sesameRect)

		# check for button click
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.gs.quit()
			elif event.type == pygame.MOUSEBUTTONUP:
				if dist(mx,my,self.pirateRect.centerx,self.pirateRect.centery)<25:
					self.circleCenter = [self.pirateRect.centerx, self.pirateRect.centery]
					self.gs.mode = pirates
					self.gs.setup()
					if self.gs.connected:
						self.gs.write('pirates')
				elif dist(mx,my,self.bballRect.centerx,self.bballRect.centery)<25:
					self.circleCenter = [self.bballRect.centerx, self.bballRect.centery]
					self.gs.mode = bball
					self.gs.setup()
					if self.gs.connected:
						self.gs.write('bball')
				elif dist(mx,my,self.otwistRect.centerx,self.otwistRect.centery)<25:
					self.circleCenter = [self.otwistRect.centerx, self.otwistRect.centery]
					self.gs.mode = otwist
					self.gs.setup()
					if self.gs.connected:
						self.gs.write('otwist')
				elif dist(mx,my,self.sesameRect.centerx,self.sesameRect.centery)<25:
					self.circleCenter = [self.sesameRect.centerx, self.sesameRect.centery]
					self.gs.mode = sesame
					self.gs.setup()
					if self.gs.connected:
						self.gs.write('sesame')

# game over screen				
class GameOver(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
	def display(self, winner):
		self.gs.screen.fill((0, 0, 0))
		# player 2 won
		if winner == 2:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			textSurf = lt.render("You lost :(", True, (255, 255, 255))
		# player 1 won
		elif winner == 1:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			textSurf = lt.render("You win! :)", True, (255, 255, 255))
		textRect = textSurf.get_rect()
		textRect.center = [200, 300]
		self.gs.screen.blit(textSurf, textRect)
		# exit from end-game screen
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.gs.quit()

# class that holds array of objects falling from sky
class Rain(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.drops = [] # list of objects
		self.created = False
	def tick(self): #create new falling item ~10% of the time
		create = random.randint(1,10)
		if create==8:
			self.created = Raindrops(self.gs)
			self.drops.append(self.created)
#			self.created = self.created.x #sent to p2
#		else:
#			self.created = False #sent to p2
		for guy in self.drops:
			guy.rect = guy.rect.move([0,1]) #all coins down 1 pixel

# class of individual objects from sky
class Raindrops(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['ball_image'])
		self.rect = self.image.get_rect()
		self.x = random.randint(30,610) #random x position for item
		self.rect.center = [self.x,-25] #starts above window

# static image of non-moving part of shooter (player 2)
class Player2Prop(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['shooter_body'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['sb_location']

# catcher (player 1)
class Player1(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['player_image'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['player_start']
		self.Moving = "N"
		self.box = Box(self.rect.center, self.gs) #player's catching receptacle
	def tick(self):
		# move player depending on key presses
		if self.Moving == "R":
			self.rect = self.rect.move([5,0])
			self.box.rect = self.box.rect.move([5,0])	
		elif self.Moving == "L":
			self.rect = self.rect.move([-5,0])
			self.box.rect = self.box.rect.move([-5,0])
		if self.rect.center[0]<self.gs.mode['max_player_left']: #can't move left anymore, put player & box at maximum left position
			self.rect.center = [self.gs.mode['max_player_left'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0]+self.gs.mode['box_offset'][0], self.rect.center[1]+self.gs.mode['box_offset'][1]]
		elif self.rect.center[0]>self.gs.mode['max_player_right']: #same as above for right
			self.rect.center = [self.gs.mode['max_player_right'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0]+self.gs.mode['box_offset'][0], self.rect.center[1]+self.gs.mode['box_offset'][1]]

# catches objects falling from sky, part of player 1
class Box(pygame.sprite.Sprite):
	def __init__(self, center, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['box_image'])
		self.rect = self.image.get_rect()
		self.x = center[0]+self.gs.mode['box_offset'][0]
		self.y = center[1]+self.gs.mode['box_offset'][1]
		self.rect.center = [self.x,self.y]

# shooter player
class Player2(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.mx = 1
		self.my = 1
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode["gun_image"])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['gun_location']
		self.lasers = []
		self.angle = 0
		#keep original image to limit resize errors
		self.orig_image = self.image

		#if I can fire laser beams, this flag will say whether I should be firing them right now
#		self.tofire = 0
	def tick(self):
		# delete lasers when the go off-screen
		for guy in self.lasers:
			if guy.rect.center[0] < -20 or guy.rect.center[0] > 660:
				self.lasers.remove(guy)	
			elif guy.rect.center[1] < -20 or guy.rect.center[1] > 500:
				self.lasers.remove(guy)
		# player 2 rotates to follow mouse (only mouse on player 2 screen though)
		self.angle = math.atan2(self.my-self.rect.center[1],self.mx-self.rect.center[0])*-180/math.pi+211.5-self.gs.mode['angle_offset']
		self.image = pygame.transform.rotate(self.orig_image, self.angle)
		self.rect = self.image.get_rect(center = self.rect.center)

# bullets that player 2 shoots
class Laser(pygame.sprite.Sprite):
	def __init__(self,x,y,xm,ym,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.xm=xm
		self.ym=ym
		self.gs = gs
		self.image = pygame.image.load("media/"+self.gs.mode['bullet_image'])
		self.rect = self.image.get_rect()
		self.rect.center=[x,y]
	def tick(self):
		# moves them across the screen at angle they were shot at
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
		self.client = client #given a reference to GameSpace
		self.queue = DeferredQueue()
	def dataReceived(self, data):
		if data == 'player 2 connected': #alerts GameSpace when p2 has connected
			self.client.connected = True
			self.client.waitingString = "p2 connected!"
			# if player 1 chooses a mode before player 2 connects
			if self.client.mode != None:
				self.transport.write(self.client.mode['name'])
		# pickled data is sent
		else:
			self.client.player2.lasers = []
			data = pickle.loads(zlib.decompress(data))
			# info about player 2's rotation
			self.client.player2.mx = data[0]
			self.client.player2.my = data[1]
			data[2] = pickle.loads(data[2]) # laser x coordinate
			data[3] = pickle.loads(data[3]) # laser y coordinate
			data[4] = pickle.loads(data[4]) # laser x slope
			data[5] = pickle.loads(data[5]) # laser y slope
			# sync laser locations with player 2
			i = 0
			for x in data[2]:
				self.client.player2.lasers.append(Laser(data[2][i], data[3][i], data[4][i], data[5][i], self.client))
				i+=1
#		if self.client.quit == 1:
#			self.transport.loseConnection()
	def connectionLost(self, reason):
		reactor.stop()
	def write(self, data): #write function used in GameSpace
		self.transport.write(data)
	def quit(self): # quit function used in GameSpace
		self.transport.loseConnection()

class ServerConnFactory(Factory):
	def __init__(self, client):
		self.client = client #given reference to GameSpace
	def buildProtocol(self, addr):
		proto = ServerConnection(addr, self.client)
		self.client.write = proto.write #sets write function in GameSpace to connection's write function
		self.client.quit = proto.quit # sets quit function in GameSpace to connection's quit function
		return proto

# main, calls game loop
if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
	lc.stop()
