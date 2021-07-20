import random
import time
import pygame
from pygame.locals import *

class Rect:
    """ 矩形を表現する．内包判定，重なり判定"""
    def __init__(self, top_left, bottom_right):
        """引数はそれぞれ長さ２のリスト([x,y])"""
        self.setDim(top_left, bottom_right)

    def setDim(self, top_left, bottom_right):
        """引数はそれぞれ長さ２のリスト([x,y])"""
        self.min = top_left
        self.max = bottom_right

    def contains(self,p):
        """点p([x,y])が内側にあるか"""
        return self.min[0] < p[0] and p[0] < self.max[0] \
           and self.min[1] < p[1] and p[1] < self.max[1]

    def len(self, i):
        """ 次元iの長さ """
        return self.max[i] - self.min[i]

    def center(self, i):
        """次元iの中心"""
        return (self.max[i] + self.min[i])/2

    def intersects(self, r):
        """矩形rと交差しているか（重なっているか）"""
        for i in range(2):
            d = abs(self.center(i)-r.center(i))
            if d > (self.len(i) + r.len(i))/2:
                return False
        return True

def add(a,b):
    return [a[0]+b[0], a[1]+b[1]]


class Entity(Rect):
    """ 登場キャラクターの既定クラス """
    def __init__(self, size:list, name:str=None, visual=None, algorithms=None):
        """ 
        Args:
            pos:位置
            size:矩形サイズ(長さ２のリスト)
            name:名前（文字列）
            visual:割り当てられるグラフィック名（文字列）
            algorithm:動きを決定するオブジェクト 
        """
        self.pos = [0,0]
        self.size = size
        self.name = name
        self.algorithms = algorithms
        self.visual = visual
        self.will_disappear = False
        self.setDim()

    def setDim(self):
        super().setDim(self.pos, add(self.pos, self.size))

    def disapper(self): 
        '''消滅させる'''
        self.will_disappear = True

    def disappeared(self):
        '''消滅予定か？ = 生きてるかどうか確認'''
        return self.will_disappear

    def getPos(self) -> list: 
        '''位置を返す'''
        return self.pos

    def setPos(self,p : list):
        """位置を設定する。pは大きさ２のリスト [0,0]のように """
        self.pos = list(p)
    
    def update(self, delta: float):
        '''更新する'''
        for a in self.algorithms:
            a.update(self,delta)

        self.setDim()

    def __str__(self):
        """print文に渡した時に表示される文字列"""
        return "entity name:{} pos:{}".format(self.name, self.pos)

class LinearMotion:
    """一定速度で動くオブジェクト"""
    def __init__(self, initial=[0,0]):
        self.vel = initial

    def getVel(self):
        return self.vel

    def setVel(self,v):
        self.vel = list(v)

    def update(self, entity, delta):
        p = entity.getPos()

        p[0] += self.vel[0] * delta
        p[1] += self.vel[1] * delta
        
        entity.setPos(p)

class AccelMotion(LinearMotion):
    """一定に加速するオブジェクト"""
    def __init__(self, vel=[0,0], acc=[0,0]):
        super().__init__(vel)
        self.acc = acc

    def update(self, entity, delta):
        super().update(entity, delta)
        acc=self.acc[:]
        acc[0] *= delta; acc[1] *= delta

        self.setVel(add(self.getVel(),acc))

class WithinScreen:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        
    def update(self, entity, delta):
        rect = Rect([0,0], self.screen_size)
        if not rect.contains(entity.getPos()):
            entity.disapper()


PLAYERS_POS = [150,450]
class Model:
    def __init__(self, view):
        self.view = view
        self.Ground = 480
        
        self.player_HP = 100
        self.player_maxHP = 100
        self.player_controller = LinearMotion()
        self.player = Entity([40,40],name="denchu",visual="player",algorithms=[self.player_controller])
        self.player.setPos(PLAYERS_POS)
        self.entites = [self.player]
        self.timer = 1
        self.algo2 = []

    def moveRight(self, velx):
        self.view.flip = False
        self.player_controller.setVel([velx,0])
    
    def moveLeft(self, velx):
        self.view.flip = True
        self.player_controller.setVel([-velx,0])

    def isOnGround(self,movable_obj):
        '''地面と接しているか'''
        if movable_obj.getPos()[1] >= self.Ground:
            return True
        else:
            return False
    
    def shoot(self):
        motion = LinearMotion()
        if self.view.flip == False:    #右
            motion.setVel([200,0])
        else:                          #左
            motion.setVel([-200,0])
        constraint = WithinScreen(self.view.getScreenSize())
        bullet = Entity([32,32], name="bullet", visual="bullet", algorithms=[motion, constraint])
        bullet.setPos(self.player.pos)
        self.entites.append(bullet)

    def shotEnemy(self, bullet, enemy):
        bullet.disapper()
        enemy.disapper()

    def interactWithEnemy(self, enemy):
        for b in filter(lambda e:e.name=="bullet", self.entites):
            if enemy.intersects(b):
                self.shotEnemy(b, enemy)

    def playerHitEnemy(self, enemy):
        if enemy.intersects(self.player):
            self.player_HP -= 20
            enemy.disapper()

    def playerGetItem(self,item):
        if item.intersects(self.player):
            self.player_HP += 20
            item.disapper()
    
    """
    def stopItem(self,item):
        if self.isOnGround(item):
            self.algo2 = [LinearMotion([0,0])] 
    """



    def update(self, delta):
        self.timer -= delta

        if self.timer < 0:
            algo = []
            algo = [LinearMotion([-40,0])]

            enemy = Entity([38,38], name="enemy", visual="robot", algorithms=algo)
            enemy.setPos([800,random.random()*self.view.getScreenSize()[0]])
            self.entites.append(enemy)

            self.algo2 = []
            self.algo2 = [LinearMotion([0,40])]            
            item = Entity([32,32], name="item", visual="egg", algorithms=self.algo2)
            item.setPos([random.random()*self.view.getScreenSize()[0],0])
            self.entites.append(item)
            
            self.timer = 3
        


        for m in self.entites[:]: #forの中でremove するためスライスでコピーを作成(google by "python for in remove ")
            m.update(delta)
            self.view.draw(self,m)

            if m.name == "enemy":
                self.interactWithEnemy(m)
                self.playerHitEnemy(m)
            
            if m.name == "item":
                self.playerGetItem(m)
                #self.stopItem(m)

            if m.disappeared():
                self.entites.remove(m)




"""
class Jumpe:
    def __init__(self, model,view):
        self.view = view
        self.model = model
        self.Ground = 450
        self.jumpCount = 20
        self.hight = 0
        self.count = 0
        self.in_air = False
        self.timer = 1

    def isOnGround(self):
        '''地面と接しているか'''
        if self.model.player.getPos()[1] >= self.Ground:
            return True
        else:
            return False

    def jumping(self):
        '''ジャンプ'''
        if (self.jumpCount > -20 and self.in_air == True):
            self.hight = self.jumpCount * abs(self.jumpCount)
            self.model.player_controller.setVel([0,-self.hight])
            self.jumpCount -= 2
        else:
            self.jumpCount = 20
            if self.isOnGround():
                self.model.player_controller.setVel([0,0])
                self.model.player.setPos([int(self.model.player.getPos()[0]),450])
                self.in_air = False

    def isjump(self):
        self.in_air = True

    def update(self, delta):
        self.timer -= delta

        if self.timer < 0:
            self.jumping()
            self.timer = 1
"""
