import numpy as np

def scoreOrdinal(answers, users, dfunc = None):
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
        highscore, winner = getWinnersOrdinal(answers)
    print (winner)
    relevantUsers = getUsers(winner, users, answers)
    return highscore, winner, relevantUsers

def getWinnersOrdinal(answers):
    length = max(answers)+2
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
        scores[a-1] = scores[a-1]+.35
        scores[a+1] = scores[a+1]+.35
        #.35 to avoid ties and don't want to overprivilige adjacent answers
    print(scores)
    winner = np.where(scores == scores.max())[0][0]
    print (winner)
    topScore = scores[winner]/(len(answers))
    print(topScore)
    return (topScore, winner)
def getWinnersNominal(answers):
    length = max(answers)+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
        #.35 to avoid ties and don't want to overprivilige adjacent answers
    print(scores)
    winner = np.where(scores == scores.max())[0][0]
    print (winner)
    topScore = scores[winner]/(len(answers))
    print(topScore)
    return (topScore, winner)

def getUsers(winner, users, answers):
    print(answers)
    print("winner")
    print(winner)
    print(answers[winner])
    rightUsers = []
    correctAnswer = answers[winner]
    for i in range(len(users)):
        if answers[i] == correctAnswer:
            rightUsers.append(users[i])
    return rightUsers

ans1 = [1,3,4,1,2,3,4,1,2,3,5,6,3,1,2,1,3,4,2,1,2,2,2,1,1,3,3]
ans2 = [1,1,1,2,2,2,1,1,1]
ans3 = [1,1,1,1,1,4,4,4,4,4]
ans4 = [1,2,2,1,2,3]
users= [6,5,4,3,2,1]
