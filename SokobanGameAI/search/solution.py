#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os #for time functions
from search import * #for search engines
from sokoban import SokobanState, Direction, PROBLEMS #for Sokoban specific classes and problems
import itertools

def sokoban_goal_state(state):
  '''
  @return: Whether all boxes are stored.
  '''
  for box in state.boxes:
    if box not in state.storage:
      return False
  return True

def manhattan_distance(box, storage):
    '''Manhattan distance: sum of horizontal and vertical distances'''
    '''INPUT: a tuple containing two tuples of positions'''
    '''OUTPUT: a numeric value of the distance between these two positions'''
    #box, storage = pair[0], pair[1]
    return abs(box[0]-storage[0]) + abs(box[1]-storage[1])

def heur_manhattan_distance(state):
#IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state. properties include: width, height, robots, boxes, storage, obstacles.'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    total_distance = 0
    for box in state.boxes: # For each box, find its nearest storage location, which can be reused for other boxes
        distances = [manhattan_distance(box, storage) for storage in state.storage]
        total_distance += min(distances)

    return total_distance

#SOKOBAN HEURISTICS
def trivial_heuristic(state):
  '''trivial admissible sokoban heuristic'''
  '''INPUT: a sokoban state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state (# of moves required to get) to the goal.'''
  count = 0
  for box in state.boxes:
    if box not in state.storage:
        count += 1
  return count

def heur_alternate(state):
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    total_distances = []
    boxes, storages = list(state.boxes), list(state.storage)
    size = len(boxes)
    box_permutations = itertools.permutations(range(0, size), size)
    # Get a permutation of the orders each box can be paired with storages
    # Loop through them to find all the possible total distances
    # This way, each box will be only paired with one storage for the final value
    for box_indices in box_permutations:
        total_distance = 0
        for i in range(0, size):
            box_index, storage_index = box_indices[i], i # boxes are permutated while storages aren't
            total_distance += manhattan_distance(boxes[box_index], storages[storage_index])
        total_distances.append(total_distance)
    # Then find the smallest total distance of all
    return min(total_distances)

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN, weight):
#IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """

    #Many searches will explore nodes (or states) that are ordered by their f-value.
    #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
    #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
    #The function must return a numeric f-value.
    #The value will determine your state's position on the Frontier list during a 'custom' search.
    #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
    return sN.gval + weight * sN.hval

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''
  se = SearchEngine('astar', 'full') # astar data structure to store the frontier, with full cycle checking

  return False

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
  se = SearchEngine('best_first', 'full')
  se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_alternate)
  final = se.search(timebound)
  return final
