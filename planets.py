#!/usr/bin/env python2.6
""" David Lopes, Kelly Gawne
This is the best game you will ever play while you are alive.
"""

import pygame
import sys
from math import atan2, degrees, sin, cos, pi, sqrt
import collections

class CelestialBody (pygame.sprite.Sprite):
    """ The base class for celestial bodies. Handles velocity, drawing, and wall bouncing."""
    def __init__ (self, gs, x=250, y=250):
        """ Sets a bunch of defaults. """
        super(CelestialBody, self).__init__()
        self.gs = gs
        self.image = self.orig_image = pygame.image.load("asteroid.png")
        self.x = x
        self.y = y
        self.velx = self.vely = 0
        self.mass = 1
        self.max_speed = 10

    def collide (self, other_body):
        """ Implement this in the subclasses to handle a collision. """
        pass

    def wall_bounce (self):
        """ Detect bounces on the edge of the screen and apply them. """
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
        """ Add velocity to position. """
        if self.velx > self.max_speed:
            self.velx = self.max_speed
        elif self.velx < -self.max_speed:
            self.velx = -self.max_speed
        if self.vely > self.max_speed:
            self.vely = self.max_speed
        elif self.vely < -self.max_speed:
            self.vely = -self.max_speed        
        self.x += self.velx
        self.y += self.vely

    def tick (self):
        """ Apply wall bouncing and velocity. """
        try:
            self.pre_tick()
        except Exception as ex:
            pass
        self.wall_bounce()
        self.apply_velocity()

    def draw (self):
        """ Draw body on the screen. """
        try:
            self.pre_draw()
        except Exception:
            pass
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
        self.mass = 10


class Ship (CelestialBody):
    def __init__ (self, gs, x=600, y=600):
        super(Ship, self).__init__(gs, x, y)
        self.image = self.orig_image = pygame.image.load("sprites/player1sprite.png")
        self.speed = 0.4
        self.mass = 10
        self.direction = 0 # in radians
        
    def handle_input (self, x, y):
        print "handling input"
        self.velx += x * self.speed
        self.vely += y * self.speed

    def pre_tick (self):
        mx, my = pygame.mouse.get_pos()
        x_dist = mx - self.x
        y_dist = self.y - my
        self.direction = atan2(y_dist, x_dist)

    def pre_draw (self):
        self.image = pygame.transform.rotate(self.orig_image, degrees(self.direction)) 


class SpringCenter:
    def __init__ (self, x, y):
        self.x = x
        self.y = y

class Forces:
    def __init__ (self, gs):
        self.gs = gs
        self.default_gravity_sources = set()
        self.default_gravity_victims = set()
        self.gravity_tuples = set()
        self.spring_tuples = {}
        
        self.G = 100
        self.K = 0.2
        self.D = 0.5

    def start_gravity (self, source=None, victim=None):
        """ Add source of gravity and a victim of gravity to the list.
        If no victim is specified, the source is added to a default list.
        It will affect all victims who are likewise placed in a default list
        if no source is specified.
        """
        if not source and not victim:
            return

        if source and not victim:
            if isinstance(source, collections.Sequence):
                for s in source:
                    self.default_gravity_sources.add(s)
            else:
                self.default_gravity_sources.add(source)
        elif victim and not source:
            if isinstance(victim, collections.Sequence):
                for v in victim:
                    self.default_gravity_victims.add(v)
            else:
                self.default_gravity_victims.add(victim)
        else:
            self.gravity_tuples.add((source, victim))

    def end_gravity (self, source=None, victim=None):
        """ Equivalent to start_gravity, but removes things from the list. """
        if not source and not victim:
            return
    
        if source and not victim:
            if source in self.default_gravity_sources:
                self.default_gravity_sources.remove(source)
        elif victim and not source:
            if victim in self.default_gravity_victims:
                self.default_gravity_victims.remove(victim)
        else:
            if (source,victim) in self.gravity_tuples:
                self.gravity_tuples.remove((source, victim))

    def start_spring (self, source=None, victim=None, eq_dist=10):
        if not source or not victim:
            return
        self.spring_tuples[(source,victim)] = eq_dist

    def end_spring (self, source=None, victim=None):
        if not source or not victim:
            return
        if (source,victim) in self.spring_tuples:
            del self.spring_tuples[(source,victim)]
        

    def apply_gravity (self, source, victim):
        vecx = source.x - victim.x
        vecy = source.y - victim.y
        mag = dist = sqrt(vecx*vecx + vecy*vecy)
        vecx /= mag
        vecy /= mag
        F = self.G*source.mass*victim.mass/(dist*dist)
     
        victim.velx += F/victim.mass * vecx
        victim.vely += F/victim.mass * vecy

    def apply_spring (self, source, victim, eq_dist):
        vecx = source.x - victim.x
        vecy = source.y - victim.y
        mag = sqrt(vecx*vecx + vecy*vecy)
        vecx /= mag
        vecy /= mag
        dist = mag-eq_dist
        F = self.K*dist
        
        dampx = victim.velx*self.D
        dampy = victim.vely*self.D

        victim.velx += F/victim.mass * vecx - dampx
        victim.vely += F/victim.mass * vecy - dampy 

    def wall_bounce (self, victim):
        pass

    def bounce (self, source, victim):
        pass

    def tick (self):
        # Apply gravities
        for source in self.default_gravity_sources:
            for victim in self.default_gravity_victims:
                self.apply_gravity(source, victim)
        for source, victim in self.gravity_tuples:
            self.apply_gravity(source, victim)

        # Apply spring forces
        for source, victim in self.spring_tuples:
            eq_dist = self.spring_tuples[(source,victim)]
            self.apply_spring(source, victim, eq_dist)

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
        self.forces = Forces(self)

        all_asteroids = [Asteroid(self,600,100)]
        all_planets = [Planet(self,100,700), Planet(self,800,100)]
        player_one = Ship(self, 200, 200)

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

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.forces.start_spring(player_one, all_asteroids[0], 100)
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                    #forces.end_spring(player_one, all_asteroids[0])
                    
            # APPLY FORCES
            self.forces.tick()

            # NOTIFY TICKS
            for a in all_asteroids:
                a.tick()
            for p in all_planets:
                p.tick()
            player_one.tick()

            # DISPLAY 
            self.screen.fill(self.black)
            for a in all_asteroids:
                a.draw()
            for p in all_planets:
                p.draw()
            player_one.draw()
            
            pygame.display.flip()


if __name__ == "__main__":
    gs = GameSpace()
    gs.main()
