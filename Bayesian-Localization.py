class BayesianLocalization(object):
    def __init__(self):
        self.stateModel = {
            -1: {-2: 0.10, -1: 0.70, 0: 0.15, 1: 0.05},
            0: {-1: 0.10, 0: 0.80, 1: 0.10},
            1: {-1: 0.05, 0: 0.15, 1: 0.70, 2: 0.10}} # P(nextState|currState, currInput)

        self.measurementModel = {"hallway": {"hallway": 0.65, "wall": 0.05, "openDoor": 0.20, "closedDoor": 0.05, "nothing": 0.05},
        "wall": {"hallway": 0.10, "wall": 0.45, "openDoor": 0.10, "closedDoor": 0.30, "nothing": 0.05},
        "openDoor": {"hallway": 0.20, "wall": 0.10, "openDoor": 0.50, "closedDoor": 0.15, "nothing": 0.05},
        "closedDoor": {"hallway": 0.05, "wall": 0.20, "openDoor": 0.15, "closedDoor": 0.55, "nothing": 0.05}} # P(measurement|currState)

        self.states = ["wall", "hallway", "wall", "closedDoor", "wall", "openDoor", "wall", "closedDoor", "wall", "hallway"] # p(x_k | z_0:k)
        self.statesUpdate = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Initial state = updated state probablities. Certainly at A
        self.inputs = [1, 1, 1, 0, 1, 1, 1, 1, 1, None] # Input u_k for each stepation
        self.measurements = [None, "hallway", "wall", "wall", "closedDoor", "wall", "wall", "openDoor", "wall", "closedDoor"]
        # Measurement z for each step

    def simulation(self, steps):
        """
            Input: total number of steps in simulation
            For each step, generate predicted probabilities of the next state and then update them with measurement z.
        """
        for step in range(steps):
            print 'Step', step, ':', [round(elem, 4) for elem in self.statesUpdate]
            statesPred = self.statePrediction(step) # x_k
            nextMeasure = self.measurements[step+1] # z_{k+1}
            self.statesUpdate = self.stateUpdate(statesPred, nextMeasure) # x_{k+1}
        print 'Step', steps, ':', [round(elem, 4) for elem in self.statesUpdate]

        maxProb = max(self.statesUpdate)
        print '\nThe robot is most likely at', self.states[self.statesUpdate.index(maxProb)], 'with', maxProb, 'confidence.\n'
        return

    def statePrediction(self, step):
        """
            Input: the current step
            Output: List of the probabilities of each state as being the true next state
                    p(x_{k+1}|z_0:k) = sum(p(x_{k+1}|x_k, u_k)*p(x_k|z_k)) (sum of all x_k's)
        """
        statesPred = []
        for nextState in range(len(self.states)):
            prob = 0;
            model = self.stateModel[self.inputs[step]] # The possible movements and their possibilities associated with the input
            for currState in range(len(self.states)):
                for changeState in model.keys():
                    if currState + changeState == nextState:
                        prob += model[changeState] * self.statesUpdate[currState]
            statesPred.append(prob)
        return statesPred

    def stateUpdate(self, statesPred, nextMeasure):
        """
            Input: List of each state's a priori probablity before that measure; the measurement
            Output: List of each state's posteriori probablity
                    p(x_{k+1}|z_{0:k+1}) = p(z_{k+1}|x_{k+1})*p(x_{k+1}|z_{0:k})/
                                           sum((p(z_{k+1}|chi_{k+1})*p(chi_{k+1}|z_{0:k})) (sum over all chi_{k+1})
        """
        statesUpdate = []
        sum = 0 # Normalization factor, denominator
        for nextState in range(len(self.states)):
            prob = self.measurementModel[self.states[nextState]][nextMeasure] * statesPred[nextState]
            statesUpdate.append(prob)
            sum += prob
        for i in range(len(statesUpdate)):
            statesUpdate[i] /=sum
        return statesUpdate

if __name__ == '__main__':
    print('Bayesian localization:\n')
    simulator = BayesianLocalization()
    print 'Probabilities at', simulator.states
    simulator.simulation(9)
