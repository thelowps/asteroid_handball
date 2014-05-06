#!/usr/bin/env python2.6

import pygame
import sys
from math import atan2, degrees, sin, cos, pi, sqrt

class CelestialBody (pygame.sprite.Sprite):
    """ The base class for celestial bodies. Handles velocity, drawing, and wall bouncing."""
    def __init__ (self, gs, x=250, y=250):
        super(CelestialBody, self).__init__()
        self.gs = gs
        self.image = self.orig_image = pygame.image.load("asteroid.png")
        self.x = x
        self.y = y
        self.velx = self.vely = 0
        self.mass = 1

    def collide (self, other_body):
        pass

    def wall_bounce (self):
        width, height = self.image.get_rect().size
        width = width/2
        height = height/2

        # Horizontally
        if self.x - width < 0 or self.x + width > self.gs.width:
            self.velx = -self.velx
            if self.x - width < 0:
                self.x = width
            else:
                self.x = self.gs.width-width

        # Vertically
        if self.y - height < 0 or self.y + height > self.gs.height:
            self.vely = -self.vely
            if self.y - height < 0:
                self.y = height
            else:
                self.y = self.gs.height-height

    def apply_velocity (self):
        self.x += self.velx
        self.y += self.vely

    def tick (self):
        self.wall_bounce()
        self.apply_velocity()

    def draw (self):
        self.gs.screen.blit(self.image, self.image.get_rect(center=(self.x,self.y)))


class Asteroid (CelestialBody):
    def __init__ (self, gs, x=250, y=250):
        super(Asteroid, self).__init__(gs, x, y)
        self.image = self.orig_image = pygame.image.load("asteroid.png")
        self.mass = 1


class Planet (CelestialBody):
    def __init__ (self, gs, x=500, y=500):
        super(Planet, self).__init__(gs, x, y)
        self.image = self.orig_image = pygame.image.load("planet.png")
        self.speed = 0.2
        self.mass = 10

    def follow_mouse (self):
        self.x, self.y = pygame.mouse.get_pos()
        
    def handle_input (self, x, y):
        self.velx += x * self.speed
        self.vely += y * self.speed


def apply_gravity (planet, asteroid):
    vecx = planet.x - asteroid.x
    vecy = planet.y - asteroid.y
    mag = sqrt(vecx*vecx + vecy*vecy)
    vecx /= mag
    vecy /= mag
    F = 100*planet.mass*asteroid.mass/(mag*mag)
     
    asteroid.velx += F/asteroid.mass * vecx
    asteroid.vely += F/asteroid.mass * vecy


class GameSpace:
    def main (self):
        # BASIC INITIALIZATION
        pygame.init()
        pygame.mixer.init() 
        
        self.size = self.width, self.height = 1000, 800
        self.black = 0,0,0

        self.screen = pygame.display.set_mode(self.size)

        pygame.key.set_repeat(25, 25)

        # GAME OBJECTS
        self.clock = pygame.time.Clock()

        # Asteroids
        all_asteroids = [Asteroid(self), Asteroid(self, 100, 600), Asteroid(self, 600, 100)]

        # Planets
        player_one = Planet(self)
        player_two = Planet(self, 700, 200)
        player_two.apply_velocity = player_two.follow_mouse
        all_planets = [player_one, player_two]

        # GAME LOOP
        while True:
            # CLOCK TICK REGULATION
            self.clock.tick(60)

            # HANDLE USER INPUT
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player_one.handle_input(0, -1)
                    elif event.key == pygame.K_DOWN:
                        player_one.handle_input(0, 1)
                    elif event.key == pygame.K_LEFT:
                        player_one.handle_input(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        player_one.handle_input(1, 0)

                    
            # APPLY FORCES
            for a in all_asteroids:
                for p in all_planets:
                    apply_gravity(p, a)

            # NOTIFY TICKS
            for a in all_asteroids:
                a.tick()
            for p in all_planets:
                p.tick()

            # DISPLAY 
            self.screen.fill(self.black)
            for a in all_asteroids:
                a.draw()
            for p in all_planets:
                p.draw()
            
            pygame.display.flip()


if __name__ == "__main__":
    gs = GameSpace()
    gs.main()
