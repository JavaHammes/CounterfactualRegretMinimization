# | RPS.py

from random import random

rock = 0
paper = 1
scissors = 2
num_actions = 3
regretSum = [0] * num_actions
strategy = [0] * num_actions 
strategySum = [0] * num_actions
oppStrategy = [0.4, 0.3, 0.3]

def getStrategy():
    normalizingSum = 0
    for a in range(num_actions):
        strategy[a] = regretSum[a] if regretSum[a] > 0 else 0
        normalizingSum += strategy[a]

    for a in range(num_actions):
        if normalizingSum > 0:
            strategy[a] /= normalizingSum
        else:
            strategy[a] = 1.0 / num_actions
        strategySum[a] += strategy[a]

    return strategy

def getAction(strategy):
    r = random()
    a = 0
    cumulativeProbability = 0
    while a < num_actions-1:
        cumulativeProbability += strategy[a]
        if r < cumulativeProbability:
            break
        a += 1

    return a

def train(iterations):
    global oppStrategy
    actionUtility = [0] * num_actions
    for i in range(iterations):
        strategy = getStrategy()
        myAction = getAction(strategy)
        otherAction = getAction(oppStrategy)
        actionUtility[otherAction] = 0
        otherAction = 0 if otherAction == num_actions - 1 else otherAction + 1
        actionUtility[otherAction] = 1
        otherAction = num_actions -1 if otherAction == 0 else otherAction - 1
        actionUtility[otherAction] = -1
        for a in range(num_actions):
            regretSum[a] += actionUtility[a] - actionUtility[myAction]
            print(regretSum)
        
def getAverageStrategy():
    avgStrategy = [0] * num_actions
    normalizingSum = 0
    for a in range(num_actions):
        normalizingSum += strategySum[a]
    for a in range(num_actions):
        if normalizingSum > 0:
            avgStrategy[a] = strategySum[a] / normalizingSum
        else:
            avgStrategy[a] = 1.0 / num_actions
    return avgStrategy


train(10000)
print(getAverageStrategy())



