# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from model import Model
#from model import Jumpe

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WIN_SIZE = (SCREEN_WIDTH,SCREEN_HEIGHT)
WIN_TITLE = "example"

RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

class View:
    def __init__(self, screen):
        self.screen = screen
        self.sprites = {}
        self.flip = False    #向き. 左がTrue,右がFalse
        self.sprites["player"] = pygame.image.load("asset/denchu.png")
        self.sprites["bullet"] = pygame.image.load("asset/batt.png")
        self.sprites["robot"] = pygame.image.load("asset/robot.png")
        self.sprites["egg"] = pygame.image.load("asset/egg.png")

    def getScreenSize(self):
        return self.screen.get_size()

    def draw(self,model, movable_obj):
        self.model = model
        img = self.sprites[movable_obj.visual]
        resized = pygame.transform.scale(img, movable_obj.size)
        #self.screen.blit(resized, movable_obj.pos)
        self.screen.blit(pygame.transform.flip(resized, self.flip, False),movable_obj.pos)

        ratio = self.model.player_HP / self.model.player_maxHP
        pygame.draw.rect(self.screen, BLACK, (10,10, 154, 24))
        pygame.draw.rect(self.screen, RED, (10,10, 150, 20))
        pygame.draw.rect(self.screen, GREEN, (10,10, 150 * ratio, 20))



class Controller:
    def __init__(self,model):    #,jumpe
        self.model = model
        #self.jumpe = jumpe
        

        self.key_down_bind = {}
        self.key_down_bind[K_LEFT] = lambda:self.model.moveLeft(100)
        self.key_down_bind[K_RIGHT] = lambda:self.model.moveRight(100)
        #self.key_down_bind[K_SPACE] = lambda:self.jumpe.isjump()
        self.key_down_bind[K_z] = lambda:self.model.shoot()

        self.key_up_bind = {}
        self.key_up_bind[K_LEFT] = lambda:self.model.moveLeft(0)
        self.key_up_bind[K_RIGHT] = lambda:self.model.moveRight(0)


    def keyDown(self, key):
        if key in self.key_down_bind:
            self.key_down_bind[key]()

    def keyUp(self, key):
        if key in self.key_up_bind:
            self.key_up_bind[key]()

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WIN_SIZE)
        pygame.display.set_caption(WIN_TITLE)

        self.view = View(self.screen)
        self.model = Model(self.view)
        #self.jumpe = Jumpe(self.model,self.view)
        self.controller = Controller(self.model)    #,self.jumpe

 
    def event_loop(self):
        clock = pygame.time.Clock()

        while True:
            clock.tick()
            for event in pygame.event.get():
                #print(event)

                if event.type == QUIT:
                    pygame.quit()
                elif event.type == KEYDOWN:
                    self.controller.keyDown(event.key)
                elif event.type == KEYUP:
                    self.controller.keyUp(event.key)

            self.screen.fill((225,255,255))    #背景色
            pygame.draw.line(self.screen,(255, 0, 0), (0, self.model.Ground), (SCREEN_WIDTH, self.model.Ground))    #地面
            self.model.update(clock.get_time()/1000)
            #self.jumpe.update(clock.get_time()/100)
            pygame.display.update()

if __name__ == "__main__":
    app = App()
    app.event_loop()
