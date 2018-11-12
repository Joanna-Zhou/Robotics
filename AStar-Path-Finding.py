"""
    Reference:
    https://www.raywenderlich.com/3016-introduction-to-a-pathfinding
    https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
"""

import numpy as np
import math
import heapq as q
# -*- coding: utf-8 -*-

class Maze(object):
    def __init__(self, size):
        self.size = size
        self.maze = np.zeros((self.size, self.size))
        self.walls = []

    def addWalls(self):
        # Bottom left
        for i in range(4, 11):
            for j in range(6, 13):
                if i + j >= 14:
                    self.maze[i,j] = 1

        # Rectangles in the centre
        self.maze[16:21, 9:13] = 1
        self.maze[11:16, 14:18] = 1
        self.maze[16:20, 18:25] = 1

        # Bottom right
        for i in range(6, 20):
            for j in range(20, 29):
                if i*8 - j*13 <= -212: # 13 y - 8 x = 212
                    self.maze[i, j] = 1

        # Top right
        self.maze[22:29, 12:29] = 1
        self.maze[22:25, 12:25] = 0

        for i in range(self.size):
            for j in range(self.size):
                if self.maze[i, j] == 1:
                    self.walls.append((i, j))
        return

    def printMaze(self):
        for i in range(self.size-1, -1, -1):
            for j in range(self.size):
                if self.maze[i, j] == 1:
                    print '.',
                elif i == 0 or i == self.size-1 or j == 0 or j == self.size-1:
                    print '.',
                else:
                    print ' ',
            print '\n',
        return

#########################################################################################

class Node(object):
    def __init__(self, position, parent):
        """
            Each node contains its parent, position (x,y), and costs g, h, f.
        """
        self.position = position
        self.x, self.y = position[0], position[1]
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

#########################################################################################

class AStar(object):
    def __init__(self, maze, start, end):
        """
            Input maze is an object in Class Maze initiated before initiating AStar
            Inputs start and end are both coordinates (x, y) representing the locations
        """
        self.maze = maze
        self.nodeStart = Node(start, None)
        self.nodeEnd = Node(end,None)
        self.path = [] # Stores the path found. To be updated only when the end node is found

        self.openQ = [] # Nodes being considered as future steps, including current node
        q.heapify(self.openQ) # Heap is used to decrease runtime
        q.heappush(self.openQ,(self.nodeStart.f, self.nodeStart))
        self.closedList = [] # Nodes already visited, not to be considered again

    def findPath(self):
        """
            [Main function] Loop until reaching the end node or there's no more walkable node
        """
        while len(self.openQ) > 0:
            # Remove the current optimal node (with the least f) from openQ to closedList
            f, nodeCurr = q.heappop(self.openQ)
            self.closedList.append(nodeCurr)
            '''
            print 'Current node:', nodeCurr.position
            print 'Open queue:', [node.position for f,node in self.openQ]
            print 'Closed list:', [node.position for f,node in self.closedList]
            '''
            # Check if the end node is reached
            if self.foundPath(nodeCurr) == True:
                return
            else: # Find its adjacent nodes and add/update them to the open list
                nodeChildren = self.findChildren(nodeCurr)
                for node in nodeChildren:
                    self.updateCosts(nodeCurr, node)
                    # If it's already in openQ, update if it's f is lower, ignore if not
                    isRepeated = False
                    for f, nodeOpen in self.openQ:
                        if nodeOpen == node:
                            isRepeated = True
                            if node.f < f:
                                self.openQ.remove((f, nodeOpen))
                                q.heappush(self.openQ,(node.f, node))
                    if isRepeated == False:
                        q.heappush(self.openQ,(node.f, node))
        return

    def findChildren(self, node):
        """
            Check all the adjacent positions and identify the walkable ones as children
        """
        nodeChildren = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = node.x + dx
                y = node.y + dy
                inClosed = False

                # Eliminate nodes: itself, walls, out of range, or on the closed list
                if x == node.x and y == node.y:
                    continue
                if x<0 or y<0 or x>self.maze.size-1 or y>self.maze.size-1:
                    continue
                if self.maze.maze[x, y] != 0:
                    continue
                for nodeClosed in self.closedList:
                    if (x, y) == nodeClosed.position:
                        inClosed = True

                # Add the walkable ones to the list
                if inClosed == False:
                    nodeChild = Node((x, y), node)
                    nodeChildren.append(nodeChild)
        return nodeChildren

    def updateCosts(self, nodeParent, nodeChild):
        """
            Calculate/update the costs g, h, and f of a given node
        """
        if nodeParent.x == nodeChild.x or nodeParent.y == nodeChild.y: # horizontal/vertical step
            nodeChild.g = nodeParent.g + 1
        else: # diagnol step
            nodeChild.g = nodeParent.g + math.sqrt(2)

        dx = abs(nodeChild.x - self.nodeEnd.x)
        dy = abs(nodeChild.y - self.nodeEnd.y)
        D, DD = 1, math.sqrt(2)
        nodeChild.h = D * max(dx, dy) + (DD-D) * min(dx, dy) # heuristics with diagnol distance

        nodeChild.f = nodeChild.g + nodeChild.h
        return

    def foundPath(self, node):
        """
            Check if the current node is the end node and retrieve the path if it is
        """
        if node == self.nodeEnd: # End goal is reached
            pathLength = 0
            child = node
            x, y = self.nodeEnd.x, self.nodeEnd.y
            while child is not None:
                self.path.append(child.position)
                if x == child.x or y == child.y:
                    pathLength += 1
                else:
                    pathLength += math.sqrt(2)
                x, y = child.x, child.y
                self.maze.maze[x, y] = 2 # For printing purpose only
                child = child.parent # Retrieve backwards

            self.path = self.path[::-1] # Reverse the path
            print 'YAY! Path is found with length', pathLength
            print self.path
            self.printPath()
            return True
        else: # End goal is not reached yet
            return False

    def printPath(self):
        size = self.maze.size
        for i in range(size-1, -1, -1):
            for j in range(size):
                if self.maze.maze[i, j] == 1: # Walls
                    print '.',
                elif self.maze.maze[i, j] == 2: # Path
                    print 'o',
                elif i == 0 or i == size-1 or j == 0 or j == size-1: # Edges
                    print '.',
                else:
                    print ' ',
            print '\n',
        return

#########################################################################################

if __name__ == "__main__":
    world = Maze(35)
    world.addWalls()
    # world.printMaze()
    start = (2, 2)
    end = (32, 32)
    pathFinding = AStar(world, start, end)
    pathFinding.findPath()
