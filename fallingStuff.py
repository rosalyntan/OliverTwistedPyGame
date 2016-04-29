#Nancy McNamara, ncmnama1

import math
import pygame
import os
import sys
from pygame.locals import *
import random

class GameSpace:
	def main(self):
		#1. basic initialization
		pygame.init()

		self.size = self.width, self.height = 640, 480
		self.background = 50, 50, 50

		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("ppprrrrooooojjjjeeeeccccttttt")
		#2. set up game objects
		self.clock = pygame.time.Clock()
		self.rain = Rain(self)
		self.player1 = Player1(self)

		#random variables in GameSpace
		self.score1 = 0
		self.keyspressed = 0
		#3. start game loop
		while 1:
			mx, my = pygame.mouse.get_pos()


			for guy in self.rain.drops:
				if pygame.sprite.collide_rect(guy, self.player1):
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
			self.screen.fill(self.background)
			lt = pygame.font.Font('freesansbold.ttf',115)
			textSurf = lt.render(str(self.score1), True, (100, 100, 100))
			TextRect = textSurf.get_rect()
			self.screen.blit(textSurf, TextRect)
			for guy in self.rain.drops:
				self.screen.blit(guy.image, guy.rect)
			self.screen.blit(self.player1.image, self.player1.rect)
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
		self.image = pygame.image.load("media/penny.png")
		self.rect = self.image.get_rect()
		self.x = random.randint(30,610)
		self.rect.center = [self.x,-25]

class Player1(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/penny.png")
		self.rect = self.image.get_rect()
		self.rect.center = [400, 300]
		self.Moving = "N"

	def tick(self):
		if self.Moving == "R":
			self.rect = self.rect.move([5,0])
		elif self.Moving == "L":
			self.rect = self.rect.move([-5,0])
		if self.rect.center[0]<20:
			self.rect.center = [20, self.rect.center[1]]
		elif self.rect.center[0]>620:
			self.rect.center = [620, self.rect.center[1]]
			

def rot_center(image, angle):
	orig_rect = image.get_rect()
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = orig_rect.copy()
	rot_rect.center = rot_image.get_rect().center
	rot_image = rot_image.subsurface(rot_rect).copy()
	return rot_image

def dist(x1, y1, x2, y2):
	return ((y2-y1)**2+(x2-x1)**2)**.5

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
