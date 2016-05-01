#Nancy McNamara, ncmnama1

import math
import pygame
import os
import sys
from pygame.locals import *
import random
from modes import pirates, otwist, bball

mode = bball

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
			#7. finally, display game object
			self.screen.blit(bg, (0,0))
			self.screen.blit(self.player1.image, self.player1.rect)
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render(str(self.score1), True, (100, 100, 100))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			self.screen.blit(self.player1.box.image, self.player1.box.rect)	
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			pygame.display.flip()


class Rain(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		self.drops = []
	def tick(self):
		create = random.randint(1,10)
		if create==8:
			self.drops.append(Raindrops())
		for guy in self.drops:
			guy.rect = guy.rect.move([0,1])

class Raindrops(pygame.sprite.Sprite):
	def __init__(self):
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
		self.box = Box(self.rect.center)
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
	def __init__(self, center):
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

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
