#!/usr/bin/env python

from __future__ import print_function

from functools import reduce
from random import randint
from sys import exit, setrecursionlimit

setrecursionlimit(10000)

try:
    from msvcrt import getch
except ImportError:
    from sys import stdin
    from termios import tcgetattr, tcsetattr, TCSADRAIN
    from tty import setraw

    def getch():
        file_descriptor = stdin.fileno()
        old_settings = tcgetattr(file_descriptor)
        try:
            setraw(file_descriptor)
            character = stdin.read(1)
        finally:
            tcsetattr(file_descriptor, TCSADRAIN, old_settings)
        return character

class GameMaze(object):
    MAZE = dict(
        goal='G',
        bomb='B',
        player='P',
        nothing='.',
    )
    COLORS = dict(
        goal='\033[33m',
        bomb='\033[91m',
        player='\033[47m',
        nothing='\033[36m',
        END='\033[0m',
    )

    def __init__(self, randomMaze=False, size=(70, 40)):
        object.__init__(self)
        self.size_x = size[0]
        self.size_y = size[1]
        self.game_maze = [x[:] for x in [['.'] * self.size_x] * self.size_y]
        for i in range(0, self.size_y):
            for j in [0, self.size_x - 1]:
                self.game_maze[i][j] = GameMaze.MAZE['bomb']
        for i in range(0, self.size_x):
            for j in [0, self.size_y - 1]:
                self.game_maze[j][i] = GameMaze.MAZE['bomb']

    def set_attribute(self, game_point, attribute):
        self.game_maze[game_point[1]][game_point[0]] = attribute

    def get_attribute(self, game_point):
        return self.game_maze[game_point[1]][game_point[0]]

    def clear_all(self, game_point):
        self.set_attribute(game_point, GameMaze.MAZE['nothing'])

    def __str__(self):
        string = ''
        for i in self.game_maze:
            for j in i:
                if j == GameMaze.MAZE['goal']:
                    string += GameMaze.COLORS['goal'] + j + GameMaze.COLORS['END'] + ' '
                elif j == GameMaze.MAZE['player']:
                    string += GameMaze.COLORS['player'] + j + GameMaze.COLORS['END'] + ' '
                elif j == GameMaze.MAZE['bomb']:
                    string += GameMaze.COLORS['bomb'] + j + GameMaze.COLORS['END'] + ' '
                elif j == GameMaze.MAZE['nothing']:
                    string += GameMaze.COLORS['nothing'] + j + GameMaze.COLORS['END'] + ' '
                else:
                    string += j + ' '
            string += '\n'
        return string

    def count_attribute(self, attribute):
        count = 0
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                if self.get_attribute((i, j)) == attribute:
                    count = count + 1
        return count

    def load(self):
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                with open(",".join(map(str,[i, j]))) as f:
                    data = f.read()
                    if data in ['B', 'G']:
                        self.set_attribute((i, j), data)
                    else:
                        self.set_attribute((i, j), '.')

    def dump(self):
        goals = []
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                if self.get_attribute((i, j)) == 'G':
                    goals.append((i, j))
        if goals == []:
            raise Exception('No Goals Found. Need atleast one Goal.')
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                with open(",".join(map(str,[i, j])), 'w') as f:
                    attribute = self.get_attribute((i, j))
                    if attribute in ['B', 'G']:
                        f.write(attribute)
                    else:
                        sum = reduce(lambda x, y: x + y, [(((((i - x[0]) ** 2) + (j - x[1]) ** 2)) ** 0.5) for x in goals])
                        f.write(str(sum))

    __repr__ = __str__

if __name__ == "__main__":
    maze = GameMaze()
    try:
        maze.load()
    except IOError:
        pass
    position = [10, 10]
    place_tile = '.'
    while True:
        print (maze)
        print ("Bomb Density : %d" % (maze.count_attribute('B')))
        print ("Place Tile : %s" % (place_tile))
        print ("Position : (%d, %d)" % tuple(position))
        character = getch()
        while character not in ['q', 'w', 'a', 's', 'd', 'B', 'G', '.']:
            character = getch()
        if character == 'q':
            maze.dump()
            exit(0)
        if character in ['B', 'G', '.']:
            place_tile = character
        if character == 'w':
            position[1] = position[1] - 1
        if character == 'a':
            position[0] = position[0] - 1
        if character == 's':
            position[1] = position[1] + 1
        if character == 'd':
            position[0] = position[0] + 1
        maze.set_attribute(position, place_tile)
