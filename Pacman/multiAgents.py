# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import random
import functools

import util
from game import Agent, Directions  # noqa
from util import manhattanDistance  # noqa

import copy # for creating deep copies of alpha and beta

_HIGH = 1000000
_LOW = -1000000
_INFINITY = float('inf')
_DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition() # Tuple (x, y)
        newFood = successorGameState.getFood() # A binary map of T/F, T indicating food
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        "If no food left, winning, so go with this option"
        newFoodPos = newFood.asList()
        newFoodNum = len(newFoodPos)
        if newFoodNum == 0: return _HIGH

        "If ghost is adjacent or at the same next grid, abandon this option"
        ghostDistances = []
        for ghostState in newGhostStates:
            if ghostState.scaredTimer == 0:
                ghostDistance = manhattanDistance(ghostState.getPosition(), newPos)
                if ghostDistance <= 1: return _LOW
                else: ghostDistances.append(ghostDistance)

        "Prefer smaller distance to closest food & smaller total amount of fruit left"
        foodDistances = []
        for foodPos in newFoodPos:
            foodDistances.append(manhattanDistance(foodPos, newPos))
        newScore = -(min(foodDistances)+50*newFoodNum)
        if newFoodNum > 1: # More than one food left
            foodDistances.remove(min(foodDistances))
            newScore -= min(foodDistances)/2

        "Punish for entering a corner that doesn't contain food"
        wallNum = 0
        for direction in _DIRECTIONS:
            if successorGameState.hasWall(newPos[0]+direction[0], newPos[1]+direction[1]) and not successorGameState.hasFood(newPos[0]+direction[0], newPos[1]+direction[1]):
                wallNum += 1
        if wallNum >= 3: newScore += _LOW/2

        "Break the tie between two states by prefering larger distance to the closest ghost"
        newScore += random.random()*(sum(ghostDistances)+0.01)/min(foodDistances)
        return newScore #successorGameState.getScore()



def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn="scoreEvaluationFunction", depth="2"):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"

        def getMinimaxVal(state, depth):
            "Terminal reached or depth reached the search depth allowed"
            if state.isWin() or state.isLose() or depth == self.depth * state.getNumAgents():
                return self.evaluationFunction(state)

            "Pacman: index = 0, Ghosts: index > 0"
            agentIndex = depth % state.getNumAgents()
            actions = state.getLegalActions(agentIndex)

            "Pacman/Ghost's move, find max/max"
            if agentIndex == 0: # Pacman
                bestVal = _LOW
                for action in actions:
                    newState = state.generateSuccessor(agentIndex, action)
                    newVal = getMinimaxVal(newState, depth+1)
                    bestVal = max(bestVal, newVal)
                return bestVal

            else: # Ghost
                bestVal = _HIGH
                for action in actions:
                    newState = state.generateSuccessor(agentIndex, action)
                    newVal = getMinimaxVal(newState, depth+1)
                    bestVal = min(bestVal, newVal)
                return bestVal

        "Determind the moves given each move's minimax value"
        legalMoves = gameState.getLegalActions()
        scores = [getMinimaxVal(state=gameState.generateSuccessor(0, action), depth=1) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best
        return legalMoves[chosenIndex]


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def getMinimaxVal(state, depth, ab):
            "Input list ab is [alpha, beta, beta...]. ab[0] is alpha for pacman and beta's being for each ghost"
            "Terminal reached or depth reached the search depth allowed"
            if state.isWin() or state.isLose() or depth == self.depth * state.getNumAgents():
                return self.evaluationFunction(state)

            "Pacman: index = 0, Ghosts: index > 0"
            agentIndex = depth % state.getNumAgents()
            "Pacman/Ghost's move, find max/max"
            if agentIndex == 0: # Pacman
                return getMaxVal(state, depth, agentIndex, ab)
            else: # Ghost
                return getMinVal(state, depth, agentIndex, ab)

        def getMaxVal(state, depth, agentIndex, ab):
            # A deep copy need to created so that the recursive calls won't change the alpha list at parent node
            localab = copy.deepcopy(ab)
            bestVal = -_INFINITY
            for action in state.getLegalActions(agentIndex):
                newState = state.generateSuccessor(agentIndex, action)
                newVal = getMinimaxVal(newState, depth+1, localab)
                bestVal = max(bestVal, newVal)
                if bestVal >= min(localab[1:]): # smallest alpha of any ghost
                    return bestVal
                localab[0] = max(localab[0], bestVal)
            return bestVal

        def getMinVal(state, depth, agentIndex, ab):
            localab = copy.deepcopy(ab)
            bestVal = _INFINITY
            for action in state.getLegalActions(agentIndex):
                newState = state.generateSuccessor(agentIndex, action)
                newVal = getMinimaxVal(newState, depth+1, localab)
                bestVal = min(bestVal, newVal)
                if bestVal <= localab[0]:
                    return bestVal
                localab[agentIndex] = min(localab[agentIndex], bestVal)
            return bestVal

        "Determind the moves given each move's minimax value"
        bestScore, bestAction = -_INFINITY, None
        ab = [-_INFINITY] + [_INFINITY for i in range(1, gameState.getNumAgents())]
        for action in gameState.getLegalActions(0):
            score = getMinimaxVal(gameState.generateSuccessor(0, action), 1, ab)
            if score > bestScore:
                bestScore, bestAction = score, action
            ab[0] = max(ab[0], bestScore) # Update the alpha of top level (depth = 0)
        return bestAction




class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        def getMinimaxVal(state, depth):
            "Input list ab is [alpha, beta, beta...]. ab[0] is alpha for pacman and beta's being for each ghost"
            "Terminal reached or depth reached the search depth allowed"
            if state.isWin() or state.isLose() or depth == self.depth * state.getNumAgents():
                return self.evaluationFunction(state)

            "Pacman: index = 0, Ghosts: index > 0"
            agentIndex = depth % state.getNumAgents()
            "Pacman/Ghost's move, find max/max"
            if agentIndex == 0: # Pacman
                return getMaxVal(state, depth, agentIndex)
            else: # Ghost
                return getMinVal(state, depth, agentIndex)

        def getMaxVal(state, depth, agentIndex):
            # A deep copy need to created so that the recursive calls won't change the alpha list at parent node
            bestVal = -_INFINITY
            for action in state.getLegalActions(agentIndex):
                newState = state.generateSuccessor(agentIndex, action)
                newVal = getMinimaxVal(newState, depth+1)
                bestVal = max(bestVal, newVal)
                if bestVal >= min(localab[1:]): # smallest alpha of any ghost
                    return bestVal
                localab[0] = max(localab[0], bestVal)
            return bestVal

        def getMinVal(state, depth, agentIndex):
            bestVal = _INFINITY
            for action in state.getLegalActions(agentIndex):
                newState = state.generateSuccessor(agentIndex, action)
                newVal = getMinimaxVal(newState, depth+1)
                bestVal = min(bestVal, newVal)
                if bestVal <= localab[0]:
                    return bestVal
            return bestVal

        "Determind the moves given each move's minimax value"
        bestScore, bestAction = -_INFINITY, None
        for action in gameState.getLegalActions(0):
            score = getMinimaxVal(gameState.generateSuccessor(0, action), 1)
            if score > bestScore:
                bestScore, bestAction = score, action
        return bestAction


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction
