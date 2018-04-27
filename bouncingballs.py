'''Program: bouncingballs.py
Provides simple event simulation using a
priority queue to check for collisions
'''

import random
import math
import heapq
import inspect
from graphics import  *

# Defines a Ball object which can be used in the Collision Simulator
class Ball:
    def __init__(self, x, y, vx, vy, r, windowWidth, windowHeight):
        self.x = x                          # position
        self.y = y                         
        self.vx = vx                        # velocity  
        self.vy = vy
        self.radius = r                     # size of Ball in pixels
        self.circle = Circle(Point(x, y), r)
        self.mass = 1                       # used for collision physics
        self.maxWidth = windowWidth         # highest possible x position
        self.maxHeight = windowHeight       # highest possible y position
        self.collisionCnt = 0               # number of pending collisions
 
    def __eq__(self, other):
        return ((self.x, self.y, self.circle) ==
                (other.x, other.y, other.circle))

    # Moves ball by time * speed
    def move(self, dt):   
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    # Draws the a Circle to window
    def draw(self, window):
        self.circle.draw(window)
    
    # Moves Circle to current position on window 
    def update(self, window):    
        self.circle.move(self.x - self.circle.getCenter().getX(), self.y - self.circle.getCenter().getY())

    # Calculates time until collision with another Ball
    def timeToHit(self, that):
        if self == that:
            return math.inf 

        # distance
        dx = that.x - self.x
        dy = that.y - self.y
        
        # speed
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy
        
        # collision prediction
        # d = (Δv*Δr)^2 − (Δv*Δv)(Δr*Δr − σ^2)
        dvdr = dx*dvx + dy*dvy
        #print(dvdr)
        if dvdr > 0: 
            return math.inf
        dvdv = dvx*dvx + dvy*dvy
        drdr = dx*dx + dy*dy
        sigma = self.radius + that.radius
        
        d = (dvdr*dvdr) - (dvdv * (drdr - sigma*sigma))
        if d <= 0: # don't want to divide by zero
            return math.inf
        #print ("collision!!!") 
        #print(-(dvdr + math.sqrt(d)) / dvdv)
        return -(dvdr + math.sqrt(d)) / dvdv

    def timeToHitVWall(self):
        if (self.vy == 0):
            return math.inf
        elif (self.vy > 0.0):
            return (self.maxHeight - self.radius - self.y) / self.vy
        elif (self.vy < 0.0):
            return (0.0 + self.radius - self.y) / self.vy

    def timeToHitHWall(self):
        if (self.vx == 0.0):
            return math.inf
        elif (self.vx > 0.0):
            return (self.maxWidth - self.radius - self.x) / self.vx
        elif (self.vx < 0.0):
            return (0.0 + self.radius - self.x) / self.vx


    # adjusts velocity vectors of two objects after a collision
    def bounceOff(self, that):
        dx = that.x - self.x
        dy = that.y - self.y
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy
        dvdr = dx*dvx + dy*dvy
        dist = self.radius + that.radius

        # calculate impulse J
        # J = 2 * mass[i] * mass[j] (Δv * Δr) / σ(mass[i] + mass[j])
        J = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)
        Jx = J * dx / dist
        Jy = J * dy / dist
        self.vx += Jx / self.mass
        self.vy += Jy / self.mass
        that.vx -= Jx / that.mass
        that.vy -= Jy / that.mass

        # increase collision count
        self.collisionCnt = self.collisionCnt + 1
        that.collisionCnt = that.collisionCnt + 1

    def bounceOffVWall(self):
        self.vy = -self.vy;
        self.collisionCnt = self.collisionCnt + 1

    def bounceOffHWall(self):
        self.vx = -self.vx; 
        self.collisionCnt = self.collisionCnt + 1


# Defines an Event that will occur at time t between objects a and b
# if neither a & b are None -> collision with another object
# if one of a or b is None -> collision with wall
# if both a & b are None -> do nothing
class Event:
    def __init__(self, t, a, b):
        self.time = t    
        self.a = a
        self.b = b
        self.countA = 0
        self.countB = 0
    
    # comparator
    def __lt__(self, that):
        return self.time <= that.time

    def isValid(self):
        if not math.isnan(self.time) and self.time < 1000:
            return True
        else:
            return False  

# Collision System used to predict when two objects will
# colide and store those events in a min priority queue.
# Also used to run simulation.
class CollisionSystem:
    def __init__(self, balls):
        self.pq = []                # priority queue    
        self.time = 0.0             # simulation clock time 
        self.balls = balls          # List of balls

    # Adds all predicted collision times with this object to priority queue
    def predict(self, a):
        if a is None:
            return
        '''
        # insert collision time with all other balls into priority queue
        for b in self.balls:
            dt = a.timeToHit(b)
            evt = Event(self.time + dt, a, b)
            if evt.isValid():
                heapq.heappush(self.pq, evt)
        '''

        # insert collision time to hit walls into priority queue
        dt = a.timeToHitVWall()/1000
        evt = Event(self.time + dt, a, None)
        if evt.isValid():
            heapq.heappush(self.pq, evt)

        dt = a.timeToHitHWall()/1000
        evt = Event(self.time + dt, None, a)   
        if evt.isValid():
            heapq.heappush(self.pq, evt) 
        

    # Inserts predicted collision times into priority queue
    # Processes the events in priority queue
    def populatePQ(self, win):
        for ball in self.balls:
            ball.draw(win)
            self.predict(ball)
        heapq.heappush(self.pq, Event(0, None, None)) # needed so pq is never empty initially

    def simulate(self, win):
        while len(self.pq) > 0: # not empty
            print(len(self.pq))
            # grab top item from priority queue
            evt = heapq.heappop(self.pq)
            print(evt.time)
            if not evt.isValid():
                continue
            a = evt.a
            b = evt.b


            # move all balls
            for ball in self.balls:
                ball.move(evt.time - self.time)
                #ball.move(.5)
            #self.time = evt.time

            if a is not None and b is not None: # object collision
                pass
                #a.bounceOff(b)
            elif a is not None and b is None:
                a.bounceOffVWall()
                pass
            elif a is None and b is not None:
                b.bounceOffHWall()
                pass
            elif a is None and b is None:
                pass
                #for ball in self.balls:
            
            for ball in self.balls:
                ball.update(win)                    

            # update all collision predictions for objects a and b
            self.predict(a)
            self.predict(b)

'''
class Pnt:
    x = 1
    y = 2

class PntHolder:
    def __init__(self, points):
        self.points = points

    def iterate(self, other):
        for each in self.points:
            print(each.x)
'''

def main():
    win = GraphWin('Bouncing Balls', 500, 500)
    win.setBackground('white')

    # Create a list of random balls
    balls = []
    n = 10
    for i in range(0, n):
        ballRadius = 5
        randX = random.uniform(0 + ballRadius, win.width - ballRadius)
        randY = random.uniform(0 + ballRadius, win.height - ballRadius)
        randVX = random.uniform(-1, 1)
        randVY = random.uniform(-1, 1)
        balls.append(Ball(randX, randY, randVX, randVY, ballRadius, win.width, win.height))
 
    cs = CollisionSystem(balls)
    cs.populatePQ(win)
    
    
    '''
    # TESTS
    b1 = Ball(1, 1, 1, 1, 5, 350, 350)
    b2 = b1
    b3 = Ball(200, 200, 1, 1, 5, 350, 350)
    e1 = Event(100, b1, b3)
    e2 = Event(200, b1, b3)
    e3 = Event(200, b1, b2)
    print(e3.isValid())
    print(Event(99999, b1, b2).isValid())
    assert 5 == 2 # check if assert is working
    assert e1 < e2
    assert e2 > e1
    assert e2 < e1 
    

    # Simulation Loop
    '''
    while win.checkMouse() is None:
        
        cs.simulate(win) 
        #pass
        #for ball in cs.balls:
            #ball.update(win)
    
    win.close



    
main()