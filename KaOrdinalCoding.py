import numpy as np
from UnitizingScoring import *
from ThresholdMatrix import *

def evaluateCoding(answers, users, starts, ends, numUsers, length, dfunc = None):
    highScore, winner, relevantUsers = scoreCoding(answers, users, dfunc)
    winner, units, uScore = passToUnitizing(answers,users,starts,ends,numUsers,length,\
        highScore, winner, relevantUsers)
    return winner, units,uScore, highScore

def passToUnitizing(answers,users,starts,ends,numUsers,length,\
    highScore, winner, relevantUsers):
    if evalThresholdMatrix(highScore, numUsers) == 'H':
        goodIndices = filterIndexByAnswer(winner, answers)
        # print("goodIndices-from answer")
        # print(goodIndices)
        # print(starts)
        #f for filtered
        starts,ends, users = np.array(starts), np.array(ends), np.array(users)
        fStarts, fEnds, fUsers = starts[goodIndices], ends[goodIndices], users[goodIndices]
        if max(fEnds)>0:
            uScore, units = scoreNickUnitizing(fStarts, fEnds, length, len(fUsers), fUsers, winner, answers)
        else:
            uScore = 'NA'
            units = []
        return winner, units, uScore
    else:
        status = evalThresholdMatrix(highScore, numUsers)
        return status,status,status


def scoreCoding(answers, users, dfunc):
    """scores coding questions using an ordinal distance
    function(defined in getWinners method)
    inputs: answers array like object of the answers for the question
            users is array-like object of users that answered
            dfunc should be 'ordinal' or 'nominal', defaults to nominal
        answers and users should be the same length
    outputs: a tuple of the highest score any answer earned, the
            'winning' answer, and a list containing userIds of
            users who chose that answer
            ordered (highest score, winning answer, userIDs)
    """
    answers = [int(a) for a in answers]
    if dfunc == 'ordinal':
        highscore, winner = getWinnersOrdinal(answers)
    else:
        highscore, winner = getWinnersNominal(answers)
    print ('winner', winner)
    relevantUsers = getUsers(winner, users, answers)
    return highscore, winner, relevantUsers

def getWinnersOrdinal(answers):
    #Shannon Entropy ordinal metric
    length = max(answers)
    #index 1 refers to answer 1, 0 and the last item are not answer choices, but
    # deal with corner cases that would cause errors
    original_arr = np.array(answers)
    aggregate_arr = np.zeros(length)
    for i in original_arr:
        aggregate_arr[i - 1] += 1
    prob_arr = aggregate_arr / sum(aggregate_arr)
    x_mean = np.mean(original_arr)
    total_dist = len(aggregate_arr)
    winner = int(np.argwhere(result == top_score))
    topScore = 1 + np.dot(prob_arr, np.log2(1 - abs(np.arange(total_dist) - x_mean) / total_dist))
    return (topScore, winner)

def getWinnersNominal(answers):
    length = max(answers)+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
    winner = np.where(scores == scores.max())[0][0]
    topScore = scores[winner]/(len(answers))
    return (topScore, winner)

def getUsers(winner, users, answers):
    print('answer:', winner)
    print(answers)
    rightUsers = []
    for i in range(len(users)):
        if answers[i] == winner:
            rightUsers.append(users[i])
    print('users:', rightUsers)
    return rightUsers

ans1 = [1,3,4,1,2,3,4,1,2,3,5,6,3,1,2,1,3,4,2,1,2,2,2,1,1,3,3]
ans2 = [1,1,1,2,2,2,1,1,1]
ans3 = [1,1,1,1,1,4,4,4,4,4]
ans4 = [1,2,2,1,2,3]
users= [6,5,4,3,2,1]
