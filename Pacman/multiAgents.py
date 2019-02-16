# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purpacmanPoses provided that (1) you do not distribute or publish
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
            if successorGameState.hasWall(newPos[0]+direction[0], newPos[1]+direction[1])\
            and not successorGameState.hasFood(newPos[0]+direction[0], newPos[1]+direction[1])\
            and newPos not in successorGameState.getCapsules():
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
        def getExpectimaxVal(state, depth):
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
                newVal = getExpectimaxVal(newState, depth+1)
                bestVal = max(bestVal, newVal)
            return bestVal

        def getMinVal(state, depth, agentIndex):
            sum, count = 0, 0
            for action in state.getLegalActions(agentIndex):
                newState = state.generateSuccessor(agentIndex, action)
                newVal = getExpectimaxVal(newState, depth+1)
                sum += newVal
                count += 1
            return float(sum)/count

        "Determind the moves given each move's minimax value"
        legalMoves = gameState.getLegalActions()
        scores = [getExpectimaxVal(state=gameState.generateSuccessor(0, action), depth=1) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best
        return legalMoves[chosenIndex]


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION:
      Essentially, the values of given state is evaluated using a linear combination of features, including:
      1. Maximizing current score (the one shown on the GUI)
      2. Minimizing numbers of food and/or capsules left
      3. Minimizing the distances from Pacman to cloest food(s)
      4. Maximizing distance fron Pacman to non-scared ghost, and minimizing that of scared ghosts

      The parameters are tuned by testing, however, some basic logics are:
      *. Pacman needs more incentive to go for capsules/scared ghosts, as they worth a lot more than the food
      *. They still needs to prioritize finishing the dots as that is the winning criteria.
      *. Therefore, one way to balance is to try different weights to see the trade offs.
      *. Another way is to set a cap of minimum distance, outside of which Pacman wouldn't care to chase the scared ghost.
      *. This other way can also be used for non-scared ghosts, so that Pacman doesn't get too frightened to eat.
      *. For tie breaking, I used not only the first but also the second closest food's distance with less weight.
    """
    "*** YOUR CODE HERE ***"
    "First check terminal state"
    if currentGameState.isWin(): return _INFINITY
    if currentGameState.isLose(): return -_INFINITY

    "1. Set base score with the current shown score"
    score = currentGameState.getScore()
    pacmanPos = currentGameState.getPacmanPosition()

    "2. Number of food and/or capsule -- Minimize"
    foodPos = currentGameState.getFood().asList()
    foodNum = len(foodPos)
    capsulePos = currentGameState.getCapsules()
    capsuleNum = len(capsulePos)

    "3. Distance to closest food and - Minimize"
    foodDistances = [manhattanDistance(food, pacmanPos) for food in foodPos]
    minFoodDistance = min(foodDistances)
    if minFoodDistance == 0: minFoodDistance = _LOW
    else:
        if foodNum == 1: minFoodDistance *= 1.49
        if foodNum > 1:
            foodDistances.remove(minFoodDistance)
            minFoodDistance += min(foodDistances)/2

    "4. Distance of non-scared ghosts -- Maximize, and that of scared ghosts -- Minimize"
    sumGhostDistance = 0
    for ghost in currentGameState.getGhostStates():
        ghostDistance = manhattanDistance(ghost.getPosition(), pacmanPos)
        if ghost.scaredTimer > 0:
            sumGhostDistance -= min(ghostDistance-8, 0)
        else:
            sumGhostDistance += min(ghostDistance-3, 0)
            if ghostDistance <= 1: sumGhostDistance -= _HIGH

    features = [score, foodNum, capsuleNum, 1./minFoodDistance, sumGhostDistance]
    weight   = [    1,     -10,        -20,                 30,               30]
    return sum(f*w for f,w in zip(features, weight)) #+ random.random()/10000

# Abbreviation
better = betterEvaluationFunction
