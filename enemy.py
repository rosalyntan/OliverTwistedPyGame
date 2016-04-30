#Nancy McNamara, Rosalyn Tan

#I HAVE NO IDEA HOW TO EVEN START THIS

import math
import pygame
import os
import sys
from pygame.locals import *

class GameSpace:
	def main(self):
		#1. basic initialization
		pygame.init()

		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		#2. set up game objects
		self.clock = pygame.time.Clock()
		self.player = Player(self)

		#3. start game loop
		while 1:
			mx, my = pygame.mouse.get_pos()

			#4. clock tick regulation (framerate)
			self.clock.tick(60)
			
			#5. handle user inputs
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					self.player.tofire = True
				if event.type == pygame.MOUSEBUTTONUP:
					self.player.tofire = False

			#6. send a tick to every game object
			self.player.tick()
			for laser in self.player.lasers:
				if (laser.tick()):
					self.player.lasers.remove(laser)
					if(self.enemy.isExploding==False):
						self.enemy.hp-=1

			#7. finally, display game object
			self.screen.fill(self.black)

			self.screen.blit(self.player.image, self.player.rect)


			for laser in self.player.lasers:
				self.screen.blit(laser.image, laser.rect)
			pygame.display.flip()

class Player(pygame.sprite.Sprite):

	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.realx = 1
		self.realy = 1
		self.gs = gs
		self.image = pygame.image.load("media/deathstar.png")
		self.rect = self.image.get_rect()
		self.lasers = []
		#keep original image to limit resize errors
		self.orig_image = self.image

		#if I can fire laser beams, this flag will say whether I should be firing them right now
		self.tofire = False
		self.isPlaying = False

	def tick(self):
		#get the mouse x and y position on the screen
		mx, my = pygame.mouse.get_pos()

		#this conditional prevents movement while firing
		if self.tofire == True:
			if self.isPlaying == False:
				self.realx=mx
				self.realy=my
				self.isPlaying=True
	
			#code to emit a laser beam block
			xSlope = self.realx-self.rect.center[0]
			ySlope = self.realy-self.rect.center[1]
			total = math.fabs(xSlope)+math.fabs(ySlope)
			self.lasers.append(Laser(self,self.rect.center[0],self.rect.center[1],xSlope/total, ySlope/total))
			
		else:	
			#code to calculate the angle between my current direction and the mouse position (see math.atan2)
			angle = math.atan2(my-self.rect.center[1],mx-self.rect.center[0])*-180/math.pi-40
			self.image = rot_center(self.orig_image, angle)	
	
			self.tofire = False

class Laser(pygame.sprite.Sprite):
	def __init__(self, gs=None, xc=320, yc=240, xm=1, ym=1):
		pygame.sprite.Sprite.__init__(self)
		xc=xc+xm*32
		yc=yc+ym*32
		self.xm=xm*10
		self.ym=ym*10
		self.gs = gs
		self.image = pygame.image.load("media/penny.png")
		self.rect = self.image.get_rect()
		self.rect.center=[xc,yc]
	

	def tick(self):
		if self.rect.center[0]<640 and self.rect.center[1]<480 and dist(self.rect.center[0],self.rect.center[1],640,480)<185:
			return True
		self.rect = self.rect.move([self.xm,self.ym])
		return False

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
