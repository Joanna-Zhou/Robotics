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
from heapq import *

_DISQUALIFY = 1000

def sokoban_goal_state(state):
  '''
  @return: Whether all boxes are stored.
  '''
  for box in state.boxes:
    if box not in state.storage:
      return False
  return True

######################################################################################################################
## Start: Manhattan Heuristics and its Helpers #######################################################################
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
## End: Manhattan Heuristics and its Helpers #########################################################################
######################################################################################################################


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


######################################################################################################################
## Start: Alternate Heuristics and its Helpers #######################################################################
def heur_alternate(state):
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    global astar_distances
    global past_distances

    if state == False:
        return float('inf')

    if state.parent == None: # Initiate the pass_heuristics dictionary when it's the first node expanded
        past_distances = {}
        astar_distances= get_astar_distances(state)

    ### Check deadlock

    ### Check if current state is already visited
    boxes, storages = list(state.boxes), list(state.storage)
    if str(boxes) in past_distances:
        box_distance = past_distances[str(boxes)]
    else:
        if is_deadlock(state, boxes, storages):
            past_distances[str(boxes)] = _DISQUALIFY
            return _DISQUALIFY

        total_distances = []
        size = len(boxes)
        box_permutations = itertools.permutations(range(size), size)
        # Get a permutation of the orders each box can be paired with storages
        # Loop through them to find all the possible total distances
        # This way, each box will be only paired with one storage for the sol value
        for box_indices in box_permutations:
            total_distance = 0
            for i in range(0, size):
                box_index, storage_index = box_indices[i], i # boxes are permutated while storages aren't
                # total_distance += manhattan_distance(boxes[box_index], storages[storage_index])
                total_distance += astar_distances[boxes[box_index], storages[storage_index]]
            total_distances.append(total_distance)
        box_distance = min(total_distances) # Then find the smallest total distance of all
        past_distances[str(boxes)] = box_distance
    return box_distance


def get_astar_distances(state): # this function should only be run once, at the start node
    astar_distances = {}
    for pos in itertools.product(range(state.width), range(state.height)):
        if not pos in state.obstacles:
            for storage in state.storage:
                astar_distances[pos, storage] = astar_distance(pos, storage, state)
    return astar_distances


def astar_distance(pos, storage, state):
    obstacles, width, height = state.obstacles, state.width, state.height
    open = [] # heapq structure, storing tuples of (fval, pos)
    closed = set() # set structure, storing positions only
    successors = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    gval_dict = {pos: 0}
    fval_dict = {pos: manhattan_distance(pos, storage)}

    is_dequalified = lambda pos, obstacles, width, height: pos in obstacles or pos[0] < 0 or pos[1] < 0 or pos[0] > width or pos[1] > height

    # astar loop
    heappush(open, (fval_dict[pos], pos)) # organize the queue in lowest fval order
    while open != []:
        curr_fval, curr_pos = heappop(open)
        if curr_pos == storage:
            return curr_fval
        closed.add(curr_pos)
        for direction in successors:
            next_pos = (curr_pos[0] + direction[0], curr_pos[1] + direction[1])
            if next_pos not in closed and not is_dequalified(next_pos, obstacles, width, height):
                gval_dict[next_pos] = gval_dict[curr_pos] + 1
                fval_dict[next_pos] = gval_dict[next_pos] + manhattan_distance(next_pos, storage)
                heappush(open, (fval_dict[next_pos], next_pos))

    return _DISQUALIFY # if simple astar can't find a path from this state to this storage, this state is disqualified


def is_deadlock(state, boxes, storages):
    '''Returns a boolean indicating if or not the input state is a deadlock one'''
    '''Note that this only checks the obvious deadlock scenarios to do a rough elimination under a reasonable time'''
    num_boxes, num_storages = len(boxes), len(storages)
    boxes = [box for box in boxes if box not in storages]
    boundary_indices = {'horizontal':[0, state.height-1], 'vertical':[0, state.width-1]}
    # returns if two positions are adjacent in the horizontal/vertical direction'''
    is_horizontal_adjacent = lambda pos1, pos2: (pos1[1] == pos2[1] and abs(pos1[0] - pos2[0]) <= 1)
    is_vertical_adjacent = lambda pos1, pos2: (pos1[0] == pos2[0] and abs(pos1[1] - pos2[1]) <= 1)
    if len(boxes) > 1:
        box_combinations = itertools.combinations(range(len(boxes)), 2)
        # Case 1: two boxes along a wall (doesn't apply to cases when there's onlt one box left)
        for (i1, i2) in box_combinations:
            if is_horizontal_adjacent(boxes[i1], boxes[i2]) and boxes[i1][1] in boundary_indices['horizontal']: return True
            if is_vertical_adjacent(boxes[i1], boxes[i2]) and boxes[i1][0] in boundary_indices['vertical']: return True

    ## Case 2: a box is in a corner
    for box in boxes:
        if box[0] in boundary_indices['vertical'] and box[1] in boundary_indices['horizontal']: return True

    ### Case 3: a box is by the wall but there's no storage alone that wall
    for wall in boundary_indices['horizontal']:
        num_box_along_wall = sum([box[1] == wall for box in boxes])
        num_storage_along_wall = sum([storage[1] == wall for storage in storages])
        if num_box_along_wall > num_storage_along_wall: return True
    for wall in boundary_indices['vertical']:
        num_box_along_wall = sum([box[0] == wall for box in boxes])
        num_storage_along_wall = sum([storage[0] == wall for storage in storages])
        if num_box_along_wall > num_storage_along_wall: return True
    return False
## End: Alternate Heuristics and its Helpers #########################################################################
######################################################################################################################


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

######################################################################################################################
## Start: Anytime Weighter Astar #####################################################################################
def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of weighted astar algorithm'''
    tic = os.times()[0]
    time, weight = 0, 0
    iter = 0

    se = SearchEngine('custom', 'full') # astar data structure to store the frontier, with full cycle checking
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_alternate, fval_function=(lambda sN: fval_function(sN, weight)))

    try:
        # Initiate the search results with the basic gbf
        sol = se.search(timebound)
        gval = sol.gval
    except: # If even the basic one can't find a solution, no need to continue
        pass
    time += os.times()[0] - tic

    while time < timebound and weight > 0 and not se.open.empty():
        tic = os.times()[0]
        if sol == False: weight += 0.5
        else: weight -= 0.25
        try:
            costbound = (gval, float('inf'), gval + heur_fn(final)) # hval is not constraint, gval is constraint by the past optimal g
            new_sol = se.search(timebound-time, costbound)
            new_gval = new_sol.gval
            if new_gval < gval:
                sol, gval = new_sol, new_gval
                sol_weight = weight
        except:
            pass
        time += os.times()[0] - tic
        iter += 1

    print('Total iterations:', iter, 'sol weight:', weight)
    return sol
## End: Anytime Weighter Astar #######################################################################################
######################################################################################################################


######################################################################################################################
## Start: Anytime Greedy Best First Search ###########################################################################
def anytime_gbfs(initial_state, heur_fn, timebound = 10):
    #IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of weighted astar algorithm'''
    tic = os.times()[0]
    time = 0

    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_alternate)

    try:
        # Initiate the search results with the basic gbf
        sol = se.search(timebound)
        gval = sol.gval
    except: # If even the basic one can't find a solution, no need to continue
        return False
    time += os.times()[0] - tic

    while time < timebound and not se.open.empty():
        tic = os.times()[0]
        try:
            costbound = (gval-1, float('inf'), float('inf')) # hval is not constraint, gval is constraint by the past optimal g
            new_sol = se.search(timebound-time, costbound)
            new_gval = new_sol.gval
            if new_gval < gval:
                sol, gval = new_sol, new_gval
        except:
            pass
        time += os.times()[0] - tic

    return sol
## End: Anytime Greedy Best First Search #############################################################################
######################################################################################################################
