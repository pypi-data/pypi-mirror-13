#!/usr/bin/env python

"""
    Generates a maze.
    Allows a cli tool for ease of editing maze.
    Upon saving the maze, it stores it in the current directory
    as a series of files.
"""

from __future__ import print_function

from functools import reduce
from sys import exit, setrecursionlimit

setrecursionlimit(10000)

try:
    from msvcrt import getch
except ImportError:
    from sys import stdin
    from termios import tcgetattr, tcsetattr, TCSADRAIN
    from tty import setraw

    def getch():
        """
            A getch for Linux Systems.
        """
        file_descriptor = stdin.fileno()
        old_settings = tcgetattr(file_descriptor)
        try:
            setraw(file_descriptor)
            character = stdin.read(1)
        finally:
            tcsetattr(file_descriptor, TCSADRAIN, old_settings)
        return character


class GameMaze(object):
    """
        A GameMaze class which creates a maze.
    """
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

    def __init__(self, size=(70, 40)):
        """
            Creates a GameMaze of size given.
        """
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
        """
            Sets the value on gamepoint to attribute.
        """
        self.game_maze[game_point[1]][game_point[0]] = attribute

    def get_attribute(self, game_point):
        """
            Returns the value on gamepoint.
        """
        return self.game_maze[game_point[1]][game_point[0]]

    def clear_all(self, game_point):
        """
            Resets the value on gamepoint to nothing.
        """
        self.set_attribute(game_point, GameMaze.MAZE['nothing'])

    def __str__(self):
        """
            Performs a string representation of the maze.
        """
        string = ''
        for i in self.game_maze:
            for j in i:
                if j == GameMaze.MAZE['goal']:
                    string += "".join([
                        GameMaze.COLORS['goal'],
                        j,
                        GameMaze.COLORS['END'],
                        ' '
                    ])
                elif j == GameMaze.MAZE['player']:
                    string += "".join([
                        GameMaze.COLORS['player'],
                        j,
                        GameMaze.COLORS['END'],
                        ' '
                    ])
                elif j == GameMaze.MAZE['bomb']:
                    string += "".join([
                        GameMaze.COLORS['bomb'],
                        j,
                        GameMaze.COLORS['END'],
                        ' '
                    ])
                elif j == GameMaze.MAZE['nothing']:
                    string += "".join([
                        GameMaze.COLORS['nothing'],
                        j,
                        GameMaze.COLORS['END'],
                        ' '
                    ])
                else:
                    string += j + ' '
            string += '\n'
        return string

    def count_attribute(self, attribute):
        """
            Returns the count of number of attribute in maze.
        """
        count = 0
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                if self.get_attribute((i, j)) == attribute:
                    count = count + 1
        return count

    def load(self):
        """
            Loads a maze from the current directory.
        """
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                with open(",".join(map(str, [i, j]))) as f:
                    data = f.read()
                    if data in ['B', 'G']:
                        self.set_attribute((i, j), data)
                    else:
                        self.set_attribute((i, j), '.')

    def dump(self):
        """
            Dumps a maze to the current directory.
        """
        goals = []
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                if self.get_attribute((i, j)) == 'G':
                    goals.append((i, j))
        if goals == []:
            raise Exception('No Goals Found. Need atleast one Goal.')
        for i in range(0, self.size_x):
            for j in range(0, self.size_y):
                with open(",".join(map(str, [i, j])), 'w') as f:
                    attribute = self.get_attribute((i, j))
                    if attribute in ['B', 'G']:
                        f.write(attribute)
                    else:
                        sum = reduce(
                            lambda x, y: x + y,
                            [(((((i - x[0]) ** 2) + (j - x[1]) ** 2)) ** 0.5) for x in goals]
                        )
                        f.write(str(sum))

    __repr__ = __str__


def main():
    """
        Main Function.
    """
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

if __name__ == "__main__":
    main()
