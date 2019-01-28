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

    global pass_box_distance
    if state.parent == None: # Initiate the pass_heuristics dictionary when it's the first node expanded
        pass_box_distance = {}

    ### Check deadlock
    boxes, storages = list(state.boxes), list(state.storage)

    ### Check if current state is already visited
    if str(boxes) in pass_box_distance:
        box_distance = pass_box_distance[str(boxes)]
    else:
        robots = list(state.robots)
        if is_deadlock(state, boxes, storages, robots):
            state.print_state()
            pass_box_distance[str(boxes)] = 1000
            return 1000

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
                total_distance += manhattan_distance(boxes[box_index], storages[storage_index])
            total_distances.append(total_distance)
        box_distance = min(total_distances) # Then find the smallest total distance of all
        pass_box_distance[str(boxes)] = box_distance

    robot_distance = sum([robot_beside_nothing(state, robot) for robot in state.robots])
    # Get the total manhattan distance of each robot to its nearest box
    # robot_distance = 0
    # for robot in state.robots: # For each box, find its nearest storage location, which can be reused for other boxes
    #     distances = [manhattan_distance(storage, robot) for storage in storages]
    #     robot_distance += min(distances)
    return box_distance + robot_distance

def robot_beside_nothing(state, robot_position):
    cost = 0
    if (robot_position[0]+1, robot_position[1])  in state.boxes:
        test = (robot_position[0]+2, robot_position[1]) in state.boxes
        if test in state.boxes or test in state.obstacles:
            cost+= 2
        else:
            return cost
    if (robot_position[0]-1, robot_position[1])  in state.boxes:
        test = (robot_position[0]-2, robot_position[1]) in state.boxes
        if test in state.boxes or test in state.obstacles:
            cost+= 2
        else:
            return cost
    if (robot_position[0], robot_position[1]+1)  in state.boxes:
        test = (robot_position[0], robot_position[1]+2) in state.boxes
        if test in state.boxes or test in state.obstacles:
            cost+= 2
        else:
            return cost
    if (robot_position[0], robot_position[1]-1)  in state.boxes:
        test = (robot_position[0], robot_position[1]-2) in state.boxes
        if test in state.boxes or test in state.obstacles:
            cost+= 2
        else:
            return cost
    cost+=1
    if (robot_position[0]+1, robot_position[1]+1)  in state.boxes:
        return cost
    if (robot_position[0]-1, robot_position[1]-1)  in state.boxes:
        return cost
    if (robot_position[0]-1, robot_position[1]+1)  in state.boxes:
        return cost
    if (robot_position[0]+1, robot_position[1]-1)  in state.boxes:
        return cost
    return cost+2


def is_deadlock(state, boxes, storages, robots):
    '''Returns a boolean indicating if or not the input state is a deadlock one'''
    '''Note that this only checks the obvious deadlock scenarios to do a rough elimination under a reasonable time'''
    num_boxes, num_storages, num_robots = len(boxes), len(storages), len(robots)
    # to_be_removed = [box for box in boxes if box in storages]
    # boxes -= to_be_removed
    boxes = [box for box in boxes if box not in storages]
    print(boxes, storages)

    boundary_indices = {'horizontal':[0, state.height-1], 'vertical':[0, state.width-1]}
    if len(boxes) > 1:
        box_combinations = itertools.combinations(range(len(boxes)), 2)
        # Case 1: two boxes along a wall (doesn't apply to cases when there's onlt one box left)
        for (i1, i2) in box_combinations:
            if is_horizontal_adjacent(boxes[i1], boxes[i2]) and boxes[i1][1] in boundary_indices['horizontal']:
                print(boxes[i1], boxes[i2], 'are adjacent to each other and wall.')
                return True
            if is_vertical_adjacent(boxes[i1], boxes[i2]) and boxes[i1][0] in boundary_indices['vertical']:
                print(boxes[i1], boxes[i2], 'are adjacent to each other and wall.')
                return True

    ## Case 2: a box is in a corner
    for box in boxes:
        if box[0] in boundary_indices['vertical'] and box[1] in boundary_indices['horizontal']:
            print('Box in corner:', box)
            return True

    ### Case 3: a box is by the wall but there's no storage alone that wall
    for wall in boundary_indices['horizontal']:
        num_box_along_wall = sum([box[1] == wall for box in boxes])
        num_storage_along_wall = sum([storage[1] == wall for storage in storages])
        if num_box_along_wall > num_storage_along_wall:
            print('Box along wall without storage:')
            return True
    for wall in boundary_indices['vertical']:
        num_box_along_wall = sum([box[0] == wall for box in boxes])
        num_storage_along_wall = sum([storage[0] == wall for storage in storages])
        if num_box_along_wall > num_storage_along_wall:
            print('Box along wall without storage:')
            return True
    return False

def is_horizontal_adjacent(pos1, pos2):
    '''returns if two positions are adjacent in the horizontal direction'''
    return (pos1[1] == pos2[1] and abs(pos1[0] - pos2[0]) <= 1)

def is_vertical_adjacent(pos1, pos2):
    '''returns if two positions are adjacent in the vertical direction'''
    return (pos1[0] == pos2[0] and abs(pos1[1] - pos2[1]) <= 1)

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


def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of weighted astar algorithm'''
    tic = os.times()[0]
    time, weight = 0, 2.1
    iter = 0

    se = SearchEngine('astar', 'full') # astar data structure to store the frontier, with full cycle checking
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
        if sol == False:
            weight *= 2
        else:
            weight /= 4
        try:
            costbound = (gval, float('inf'), float('inf')) # hval is not constraint, gval is constraint by the past optimal g
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
            costbound = (gval, float('inf'), float('inf')) # hval is not constraint, gval is constraint by the past optimal g
            new_sol = se.search(timebound-time, costbound)
            new_gval = new_sol.gval
            if new_gval < gval:
                sol, gval = new_sol, new_gval
        except:
            pass
        time += os.times()[0] - tic
        iter += 1

    return sol
