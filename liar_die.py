# | liar_die.py
# | simplification of the game liar dice

import random
import numpy as np

DOUBT = 0
ACCEPT = 1
#sides = None
#responseNodes = None
#claimNodes = None


'''
def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)

ar = np.array([1, 2, 3, 4, 5])

ar_n = normalized(ar)

print(ar_n)
'''


class Node:

    def __init__(self, numActions):
        self.regretSum = [0] * numActions
        self.strategy = [0] * numActions
        self.strategySum = [0] * numActions
        self.pPlayer = 0
        self.pOpponent = 0
        self.u = 0

    def getStrategy(self):
        normalizingSum = 0
        for a in range(len(self.strategy)):
            self.strategy[a] = max(self.regretSum[a], 0)
            normalizingSum += self.strategy[a]

        for a in range(len(self.strategy)):
            if normalizingSum > 0:
                self.strategy[a] /= normalizingSum
            else:
                self.strategy[a] = 1.0/len(self.strategy)

        for a in range(len(self.strategy)):
            self.strategySum[a] += self.pPlayer * self.strategy[a]
        return self.strategy

    def getAverageStrategy(self):
        normalizingSum = 0
        for a in range(len(self.strategySum)):
            normalizingSum += self.strategySum[a]
        for a in range(len(self.strategySum)):
            if normalizingSum > 0:
                self.strategySum[a] /= normalizingSum
            else:
                self.strategySum[a] = 1.0/len(self.strategySum)
        return self.strategySum


class LiarDieTrainer:

    def __init__(self, sides):
        self.sides = sides
        self.responseNodes = [[None]*(self.sides+1) for i in range(self.sides)]
        for myClaim in range(self.sides+1):
            for oppClaim in range(myClaim+1,self.sides+1):
                x = 2
                if oppClaim == 0 or oppClaim == self.sides:
                    x = 1
                self.responseNodes[myClaim][oppClaim] = Node(x)
        self.claimNodes = [[None]*(self.sides+1) for i in range(self.sides)]
        for oppClaim in range(self.sides):
            for roll in range(1, self.sides +1):
                self.claimNodes[oppClaim][roll] = Node(self.sides - oppClaim)

    def train(self, iterations):
        regret = [0] * self.sides
        rollAfterAcceptingClaim = [0] * self.sides
        for i in range(iterations):
            # Initialize rolls and starting probalities
            for i in range(len(rollAfterAcceptingClaim)):
                rollAfterAcceptingClaim[i] = random.randint(0, self.sides) + 1
            self.claimNodes[0][rollAfterAcceptingClaim[0]].pPlayer = 1
            self.claimNodes[0][rollAfterAcceptingClaim[0]].pOpponent = 1
            # Accumulate realization weights forward
            for oppClaim in range(self.sides+1):
                # Visit respone nodes forward
                if oppClaim > 0:
                    for myClaim in range(oppClaim):
                        node = self.responseNodes[myClaim][oppClaim]
                        actionProb = node.getStrategy()
                        if oppClaim < self.sides:
                            nextNode = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                            nextNode.pPlayer += actionProb[1] * node.pPlayer
                            nextNode.pOpponent += node.pOpponent
                        myClaim += 1
                # Visit claim nodes forward
                if oppClaim < self.sides:
                    node = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                    actionProb = node.getStrategy()
                    for myClaim in range(oppClaim +1, self.sides + 1):
                        nextClaimProb = actionProb[myClaim - oppClaim - 1]
                        if nextClaimProb > 0:
                            nextNode = self.responseNodes[oppClaim][myClaim]
                            nextNode.pPlayer += node.pOpponent
                            nextNode.pOpponent += nextClaimProb * node.pPlayer
            # Backpropagate utilitites, adjusting regrets and strategies
            for oppClaim in reversed(range(self.sides)):
                # Visit claim nodes backward
                if oppClaim < self.sides:
                    node = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                    actionProb = node.strategy
                    node.u = 0.0
                    for myClaim in range(oppClaim + 1, self.sides + 1):
                        actionIndex = myClaim - oppClaim - 1
                        nextNode = self.responseNodes[oppClaim][myClaim]
                        childUtil = -nextNode.u
                        regret[actionIndex] = childUtil
                        node.u += actionProb[actionIndex] * childUtil
                    for a in range(len(actionProb)):
                        regret[a] -= node.u
                        node.regretSum[a] += node.pOpponent * regret[a]
                    node.pPlayer = node.pOpponent = 0
                # Visit respone nodes backward
                if oppClaim > 0:
                    for myClaim in range(oppClaim):
                        node = self.responseNodes[myClaim][oppClaim]
                        actionProb = node.strategy
                        node.u = 0.0
                        doubtUtil = 1 if oppClaim > rollAfterAcceptingClaim[myClaim] else -1
                        regret[DOUBT] = doubtUtil
                        node.u += actionProb[0] * doubtUtil
                        if oppClaim < self.sides:
                            nextNode = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                            regret[ACCEPT] = nextNode.u
                            node.u += actionProb[ACCEPT] * nextNode.u
                        for a in range(len(actionProb)):
                            regret[a] -= node.u
                            node.regretSum[a] += node.pOpponent * regret[a]
                        node.pPlayer = node.pOpponent = 0
            # Reset strategy sums after half of training
            if i == iterations / 2:
                for nodes in self.responseNodes:
                    for node in nodes:
                        if node != None:
                            for a in range(len(node.strategySum)):
                                node.strategySum[a] = 0
                for nodes in self.claimNodes:
                    for node in nodes:
                        if node != None:
                            for a in range(len(node.strategySum)):
                                node.strategySum[a] = 0
        for initialRoll in range(1, self.sides +1):
            print(f"Initial claim policy rolll with roll {initialRoll}")
            for prob in self.claimNodes[0][initialRoll].getAverageStrategy():
                print(prob)
            print(" ")
        print("Old Claim    New Claim   Action Probabilities")
        for myClaim in range(self.sides+1):
            for oppClaim in range(myClaim+1, self.sides+1):
                print("     ", myClaim, "       ", oppClaim, "       ", self.responseNodes[myClaim][oppClaim].getAverageStrategy())
        print("Old Claim    Roll    Action Probabilities")
        for oppClaim in range(self.sides):
            for roll in range(1, self.sides +1):
                print("     ", oppClaim, "      ", roll, "      ", self.claimNodes[oppClaim][roll].getAverageStrategy())


if __name__ == '__main__':
    trainer = LiarDieTrainer(6)
    trainer.train(1)

