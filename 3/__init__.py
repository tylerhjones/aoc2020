import re
import pykka
import itertools
import util
import math
from fastcore import utils
import operator
import traceback

class TreeLocator(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.trees = set()
        self.row = 0
    
    def add_row(self, input_row):
        input_row = list(input_row) # explode string
        tree = '#'
        for i in range(len(input_row)):
            if input_row[i] == tree:
                new_cord = (i,self.row)
                # print(new_cord)
                self.trees.add(new_cord) # x,y cord for tree
        self.row += 1 # advance y

    def collides(self, cord):
        return cord in self.trees

class LocationTracker(pykka.ThreadingActor):
    def __init__(self, x_max, x_diff, y_max, y_diff):
        super().__init__()
        utils.store_attr()
        self.current = (0,0)
    
    def get_next(self):
        new_x = None
        new_y = self.current[1]+self.y_diff
        if new_y > self.y_max:
            return None

        cur_x = self.current[0]
        if cur_x+self.x_diff>=self.x_max:
            new_x = self.x_diff-(self.x_max-cur_x)
        else:
            new_x = cur_x+self.x_diff

        self.current = (new_x, new_y)
        return (new_x, new_y)

class CollisionCounter(pykka.ThreadingActor):
    def __init__(self, loc_tracker, tree_locater):
        super().__init__()
        utils.store_attr()
        
    def get_collisions(self):
        count = 0
        while True:
            loc = self.loc_tracker.get_next().get()
            if not loc:
                return count
            
            if self.tree_locater.collides(loc).get():
                count+=1


def main(inputfile):
    trees = TreeLocator.start().proxy()
    x_max = None
    y_max = 0
    with open(inputfile, 'r') as f:
        for row in f:
            if not x_max:
                x_max = len(row)-1
            trees.add_row(row)
            y_max+=1

    counts = []
    for c in [(1,1),(3,1),(5,1),(7,1),(1,2)]:
        lt = LocationTracker.start(x_max, c[0], y_max, c[1]).proxy()
        cc = CollisionCounter.start(lt, trees).proxy()
        counts.append(cc.get_collisions())


    print("Y MAX: %s" % y_max)
    print("X MAX: %s" % x_max)
    r = pykka.get_all(counts)
    print(r)
    print(math.prod(r))
    pykka.ActorRegistry.stop_all()
