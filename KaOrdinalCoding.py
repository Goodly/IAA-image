from UnitizingScoring import *
from ThresholdMatrix import *

def evaluateCoding(answers, users, starts, ends, numUsers, length, dfunc = None):
    highScore, winner, relevantUsers = scoreCoding(answers, users, dfunc)
    if dfunc == 'ordinal':
        # This functions as an outlier test, if 4 users categorizes as 'very likely' and one categorizes as
        # 'very not likely', it will fail the threshold matrix test, this method, while not rigorous, provides
        # some defense against outliers that likely were produced by trolls, misunderstandings of the question,
        # and misclicks
        if evalThresholdMatrix(highScore, numUsers)!='H':
            highScore, winner, relevantUsers = scoreCoding(answers, users, 'nominal')
    winner, units, uScore, iScore = passToUnitizing(answers,users,starts,ends,numUsers,length,\
        highScore, winner, relevantUsers)
    return winner, units, uScore, iScore, highScore

def passToUnitizing(answers,users,starts,ends,numUsers,length,\
    highScore, winner, relevantUsers):
    if evalThresholdMatrix(highScore, numUsers) == 'H':
        goodIndices = filterIndexByAnswer(winner, answers)
        #f for filtered
        starts,ends, users = np.array(starts), np.array(ends), np.array(users)
        fStarts, fEnds, fUsers = starts[goodIndices], ends[goodIndices], users[goodIndices]
        fNumUsers = len(np.unique(fUsers))
        if max(fEnds)>0:
            uScore, iScore, units = scoreNickUnitizing(fStarts, fEnds, length, fNumUsers, fUsers, winner, answers)
        else:
            uScore = 'NA'
            iScore = 'NA'
            units = []
        return winner, units, uScore, iScore
    else:
        status = evalThresholdMatrix(highScore, numUsers)
        return status,status,status, status


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
    relevantUsers = getUsers(winner, users, answers)
    return highscore, winner, relevantUsers

def getWinnersOrdinal(answers):
    #Shannon Entropy ordinal metric
    length = 5
    #index 1 refers to answer 1, 0 and the last item are not answer choices, but
    # deal with corner cases that would cause errors
    original_arr = np.array(answers) - 1
    aggregate_arr = np.zeros(length)
    for i in original_arr:
        aggregate_arr[i] += 1
    topScore, winner = shannon_ordinal_metric(original_arr, aggregate_arr)
    return (topScore, winner + 1)

def shannon_ordinal_metric(original_arr, aggregate_arr):
    original_arr = np.array(original_arr)
    aggregate_arr = np.array(aggregate_arr)
    prob_arr = aggregate_arr / sum(aggregate_arr)
    x_mean = np.mean(original_arr)
    total_dist = len(aggregate_arr)
    score = 1 + np.dot(prob_arr, np.log2(1 - abs(np.arange(total_dist) - x_mean) / total_dist))
    print('Winner: ' + str(np.where(aggregate_arr == aggregate_arr.max())[0][0]))
    print('Top Score: ' + str(score))
    winner = np.where(aggregate_arr == aggregate_arr.max())[0][0]
    return score, winner

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
    rightUsers = []
    for i in range(len(users)):
        if answers[i] == winner:
            rightUsers.append(users[i])
    return rightUsers
