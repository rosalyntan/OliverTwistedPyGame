#Nancy McNamara, ncmnama1

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
		self.background = 50, 50, 50

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

			#6. send a tick to every game object
			self.player.tick()
			#7. finally, display game object
			self.screen.fill(self.background)

			self.screen.blit(self.player.image, self.player.rect)

			pygame.display.flip()

#so we have a class where

class Player(pygame.sprite.Sprite):

	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/penny.png")
		self.rect = self.image.get_rect()

		#keep original image to limit resize errors
		self.orig_image = self.image


	def tick(self):
		#get the mouse x and y position on the screen
		mx, my = pygame.mouse.get_pos()
		self.rect = self.rect.move([1,1])


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
