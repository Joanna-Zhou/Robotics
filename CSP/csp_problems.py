from csp import Constraint, Variable, CSP
from constraints import *
from backtracking import bt_search
import util

from itertools import combinations


##################################################################
### NQUEENS
##################################################################

def nQueens(n, model):
    '''Return an n-queens CSP, optionally use tableContraints'''
    #your implementation for Question 4 changes this function
    #implement handling of model == 'alldiff'
    if not model in ['table', 'alldiff', 'row']:
        print("Error wrong sudoku model specified {}. Must be one of {}").format(
            model, ['table', 'alldiff', 'row'])

    i = 0
    dom = []
    for i in range(n):
        dom.append(i+1)

    vars = []
    for i in dom:
        vars.append(Variable('Q{}'.format(i), dom))

    cons = []

    if model == 'alldiff':
        con = AllDiffConstraint("C(Q{Columns})", vars)
        cons.append(con)
        for qi in range(len(dom)):
            for qj in range(qi+1, len(dom)):
                con = NeqConstraint("C(Q{},Q{})".format(qi,qj),
                                            [vars[qi], vars[qj]], qi, qj)
                cons.append(con)

    else:
        constructor = QueensTableConstraint if model == 'table' else QueensConstraint
        for qi in range(len(dom)):
            for qj in range(qi+1, len(dom)):
                con = constructor("C(Q{},Q{})".format(qi+1,qj+1),
                                            vars[qi], vars[qj], qi+1, qj+1)
                cons.append(con)

    csp = CSP("{}-Queens".format(n), vars, cons)
    return csp

def solve_nQueens(n, algo, allsolns, model='row', variableHeuristic='fixed', trace=False):
    '''Create and solve an nQueens CSP problem. The first
       parameer is 'n' the number of queens in the problem,
       The second specifies the search algorithm to use (one
       of 'BT', 'FC', or 'GAC'), the third specifies if
       all solutions are to be found or just one, variableHeuristic
       specfies how the next variable is to be selected
       'random' at random, 'fixed' in a fixed order, 'mrv'
       minimum remaining values. Finally 'trace' if specified to be
       'True' will generate some output as the search progresses.
    '''
    csp = nQueens(n, model)
    solutions, num_nodes = bt_search(algo, csp, variableHeuristic, allsolns, trace)
    print("Explored {} nodes".format(num_nodes))
    if len(solutions) == 0:
        print("No solutions to {} found".format(csp.name()))
    else:
       print("Solutions to {}:".format(csp.name()))
       i = 0
       for s in solutions:
           i += 1
           print("Solution #{}: ".format(i)),
           for (var,val) in s:
               print("{} = {}, ".format(var.name(),val), end='')
           print("")


##################################################################
### Class Scheduling
##################################################################

NOCLASS='NOCLASS'
LEC='LEC'
TUT='TUT'
class ScheduleProblem:
    '''Class to hold an instance of the class scheduling problem.
       defined by the following data items
       a) A list of courses to take --- vairables

       b) A list of classes with their course codes, buildings, time slots, class types,
          and sections. It is specified as a string with the following pattern:
          <course_code>- --- course code + class_type together is like nQueen
          <building>- --- pairwise, two buildings must be True with function "connected_buildings"
          <time_slot>- --- pairwise, can't be equal + if the course code is the same, must have lecture first
          <class_type>- --- if tutorial
          <section>

          An example of a class would be: CSC384-BA-10-LEC-01
          Note: Time slot starts from 1. Ensure you don't make off by one error!

       c) A list of buildings

       d) A positive integer N indicating number of time slots

       e) A list of pairs of buildings (b1, b2) such that b1 and b2 are close
          enough for two consecutive classes.

       f) A positive integer K specifying the minimum rest frequency. That is,
          if K = 4, then at least one out of every contiguous sequence of 4
          time slots must be a NOCLASS.

        See class_scheduling.py for examples of the use of this class.
    '''

    def __init__(self, courses, classes, buildings, num_time_slots, connected_buildings,
        min_rest_frequency):
        #do some data checks
        for class_info in classes:
            info = class_info.split('-')
            if info[0] not in courses:
                print("ScheduleProblem Error, classes list contains a non-course", info[0])
            if info[3] not in [LEC, TUT]:
                print("ScheduleProblem Error, classes list contains a non-lecture and non-tutorial", info[1])
            if int(info[2]) > num_time_slots or int(info[2]) <= 0:
                print("ScheduleProblem Error, classes list  contains an invalid class time", info[2])
            if info[1] not in buildings:
                print("ScheduleProblem Error, classes list  contains a non-building", info[3])

        for (b1, b2) in connected_buildings:
            if b1 not in buildings or b2 not in buildings:
                print("ScheduleProblem Error, connected_buildings contains pair with non-building (", b1, ",", b2, ")")

        if num_time_slots <= 0:
            print("ScheduleProblem Error, num_time_slots must be greater than 0")

        if min_rest_frequency <= 0:
            print("ScheduleProblem Error, min_rest_frequency must be greater than 0")

        #assign variables
        self.courses = courses
        self.classes = classes
        self.buildings = buildings
        self.num_time_slots = num_time_slots
        self._connected_buildings = dict()
        self.min_rest_frequency = min_rest_frequency

        #now convert connected_buildings to a dictionary that can be index by building.
        for b in buildings:
            self._connected_buildings.setdefault(b, [b])

        for (b1, b2) in connected_buildings:
            self._connected_buildings[b1].append(b2)
            self._connected_buildings[b2].append(b1)

    #some useful access functions
    def connected_buildings(self, building):
        '''Return list of buildings that are connected from specified building'''
        return self._connected_buildings[building]


def schedules_csp(sp):
    '''
    sp.courses = courses
    sp.classes = classes
    sp.buildings = buildings
    sp.num_time_slots = num_time_slots
    sp._connected_buildings = dict()
    sp.min_rest_frequency = min_rest_frequency
    '''

    "Define the domain and variables"
    classDom = [] # class in form of 'CSC108-BA-1-LEC-01'
    courses_sessions = []
    for class_info in sp.classes:
        classDom.append(class_info)
        courses_session = class_info.split('-')[0] + class_info.split('-')[3]
        if courses_session not in courses_sessions:
            courses_sessions.append(courses_session)

    # "Add a number of none classes to ones that have classes"
    # num_noclass = sp.num_time_slots - len(courses_sessions)
    for i in range(num_noclass):
        classDom.append(NOCLASS+'-'+str(i))

    timeVars = []
    for i in range(sp.num_time_slots):
        timeVars.append(Variable('Time-{}'.format(i+1), classDom))

    "Construct the constraints"
    cons = []

    con = AllDiffConstraint("Alldiff", timeVars)
    cons.append(con)

    for slot in range(sp.num_time_slots - sp.min_rest_frequency):
        con = NoclassConstraint("C(Time{} to Time{})".format(slot+1,slot+sp.min_rest_frequency+1), timeVars[slot+1:slot+sp.min_rest_frequency+1], 1, sp.min_rest_frequency)
        cons.append(con)

    timeslot_pairs = combinations(list(range(sp.num_time_slots)), 2)
    for (slot1, slot2) in timeslot_pairs:
        con = BinaryClassConstraint("C(Time{},Time{})".format(slot1,slot2), [timeVars[slot1], timeVars[slot2]], sp)
        cons.append(con)

    csp = CSP("{}-ClassScheduling".format(sp.num_time_slots), timeVars, cons)
    return csp


def solve_schedules(schedule_problem, algo, allsolns,
                 variableHeuristic='mrv', silent=False, trace=False):
    #If the silent parameter is set to True
    #you must ensure that you do not execute any print statements
    #in this function.

    #So if you have any debugging print statements make sure you
    #only execute them "if not silent". (The autograder will call
    #this function with silent=True, class_scheduling.py will call
    #this function with silent=False)

    #You can optionally ignore the trace parameter
    #If you implemented tracing in your FC and GAC implementations
    #you can set this argument to True for debugging.

    #Once you have implemented this function you should be able to
    #run class_scheduling.py to solve the test problems (or the autograder).

    '''This function takes a schedule_problem (an instance of ScheduleProblem
       class) as input. It constructs a CSP, solves the CSP with bt_search
       (using the options passed to it), and then from the set of CSP
       solution(s) it constructs a list (of lists) specifying possible schedule(s)
       for the student and returns that list (of lists)

       The required format of the list is:
       L[0], ..., L[N] is the sequence of class (or NOCLASS) assigned to the student.

       In the case of all solutions, we will have a list of lists, where the inner
       element (a possible schedule) follows the format above.
    '''

    #BUILD your CSP here and store it in the varable csp
    csp = schedules_csp(schedule_problem)

    #invoke search with the passed parameters
    solutions, num_nodes = bt_search(algo, csp, variableHeuristic, allsolns, trace)

    #Convert each solution into a list of lists specifying a schedule
    #for each student in the format described above.

    solutionList = []
    if len(solutions) == 0:
        # print("No solutions to {} found".format(csp.name()))
        return []
    else:
        for s in solutions:
            sList = []
            for (var,val) in s:
                if val.split('-')[0] == NOCLASS:
                    val = NOCLASS
                sList.append(val)
            if sList not in solutionList:
                solutionList.append(sList)
    return solutionList


################################################################################################
############ Binary constraint #################################################################
class BinaryClassConstraint(Constraint):
    '''BinaryClassConstraints between two variables'''
    def __init__(self, name, scope, sp):
        if len(scope) != 2:
            print("Error BinaryClassConstraint are only between two variables")
        Constraint.__init__(self,name, scope)
        self._name = "BinaryCnstr_" + name
        self.sp = sp

    def binaryCheck(self, class0, class1, timeslot0, timeslot1):
        class_info0, class_info1 = class0.split('-'), class1.split('-')
        if class_info0[0] == NOCLASS or class_info1[0] == NOCLASS:
            return True
        elif class_info0[2] != timeslot0 or class_info1[2] != timeslot1:
            "Must have time slots corresponded"
            # print('Time slot checking:', timeslot0, timeslot1, class0, class1)
            return False
        elif class_info0[0] == class_info1[0]:
            if class_info0[3] == class_info1[3]:
                "Must have diff course or diff session"
                return False
            else:
                "Must have lecture before tutorial, if same course"
                if class_info0[3] == LEC:
                    lectime, tuttime = class_info0[2], class_info1[2]
                elif class_info1[3] == LEC:
                    lectime, tuttime = class_info1[2], class_info0[2]
                if int(lectime) > int(tuttime):
                    return False
        if class_info0[0] != NOCLASS and class_info1[0] != NOCLASS and abs(int(class_info0[2]) - int(class_info1[2])) == 1:
            b0, b1 = class_info0[1], class_info1[1]
            "2 adjacent class must be in 2 close buildings"
            if b1 not in self.sp.connected_buildings(b0):
                return False
        return True

    def check(self):
        v0 = self.scope()[0]
        v1 = self.scope()[1]
        if not v0.isAssigned() or not v1.isAssigned():
            print('Not assigned yet')
            return True
        else:
            timeslot0, timeslot1 = self.v0._name.split('-')[-1], self.v1._name.split('-')[-1]
            return self.checkbinary(self, class0, class1, timeslot0, timeslot1)

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint'''
        #hasSupport for this constraint is easier as we only have one
        #other variable in the constraint.
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        otherVar = self.scope()[0]
        timeslot0, timeslot1 = var._name.split('-')[-1], otherVar._name.split('-')[-1]
        if otherVar == var:
            otherVar = self.scope()[1]
            timeslot1 = otherVar._name.split('-')[-1]
        for otherVal in otherVar.curDomain():
            if self.binaryCheck(val, otherVal, timeslot0, timeslot1):
                return True
        return False

def findvals(remainingVars, assignment, finalTestfn, partialTestfn=lambda x: True):
    '''Helper function for finding an assignment to the variables of a constraint
       that together with var=val satisfy the constraint. That is, this
       function looks for a supporing tuple.

       findvals uses recursion to build up a complete assignment, one value
       from every variable's current domain, along with var=val.

       It tries all ways of constructing such an assignment (using
       a recursive depth-first search).

       If partialTestfn is supplied, it will use this function to test
       all partial assignments---if the function returns False
       it will terminate trying to grow that assignment.

       It will test all full assignments to "allVars" using finalTestfn
       returning once it finds a full assignment that passes this test.

       returns True if it finds a suitable full assignment, False if none
       exist. (yes we are using an algorithm that is exactly like backtracking!)'''

    #sort the variables call the internal version with the variables sorted
    remainingVars.sort(reverse=True, key=lambda v: v.curDomainSize())
    return findvals_(remainingVars, assignment, finalTestfn, partialTestfn)

def findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
    '''findvals_ internal function with remainingVars sorted by the size of
       their current domain'''
    if len(remainingVars) == 0:
        return finalTestfn(assignment)
    var = remainingVars.pop()
    for val in var.curDomain():
        assignment.append((var, val))
        if partialTestfn(assignment):
            if findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
                return True
        assignment.pop()   #(var,val) didn't work since we didn't do the return
    remainingVars.append(var)
    return False


################################################################################################
############ NValue constraint #################################################################
class NoclassConstraint(Constraint):
    '''NValues constraint over a set of variables.  Among the variables in
       the constraint's scope the number that have been assigned
       values in the set 'required_values' is in the range
       [lower_bound, upper_bound] (lower_bound <= #of variables
       assigned 'required_value' <= upper_bound)

       For example, if we have 4 variables V1, V2, V3, V4, each with
       domain [1, 2, 3, 4], then the call
       NValuesConstraint('test_nvalues', [V1, V2, V3, V4], [3,2], 2,
       3) will only be satisfied by assignments such that at least 2
       the V1, V2, V3, V4 are assigned the value 3 or 2, and at most 3
       of them have been assigned the value 3 or 2.

    '''

    #Question 5 you have to complete the implementation of
    #check() and hasSupport. You can change __init__ if you want
    #but do not change its parameters.

    def __init__(self, name, scope, lower_bound, upper_bound):
        Constraint.__init__(self,name, scope)
        self._name = "NValues_" + name
        self._lb = lower_bound
        self._ub = upper_bound

    def check(self):
        '''True if the number of values in the required values are within the range of lower and upper bound
        '''
        count = sum(1 for var in self.scope() if var.getValue().split('-')[0] == NOCLASS)
        return self._lb <= count <= self._ub

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint

           HINT: check the implementation of AllDiffConstraint.hasSupport
                 a similar approach is applicable here (but of course
                 there are other ways as well)
        '''
        if var not in self.scope():
            return True

        def valsNotEqual(l):
            '''tests a list of assignments which are pairs (var,val)
               to see if they can satisfy the constraint (in the same way was the check function)'''
            count = sum(1 for (var, val) in l if val.split('-')[0] == NOCLASS)
            return self._lb <= count <= self._ub

        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], valsNotEqual)
        return x
