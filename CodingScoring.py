from UnitizingScoring import *
from ThresholdMatrix import *
from data_utils import *
from math import floor

def evaluateCoding(answers, users, starts, ends, numUsers, length, dfunc = None):
    """ calculate all scores for any coding question
        inputs:
        answers, users, starts, and ends are all lists that are in the same order,
        meaning that index 0 of each list refers to the user at any index selected one answer, one startpoint, and
        one endpoint being evaluated, it is possible for users to appear in the list multiple times, for instance
        if they highlighted multiple portions of the text or chose more than one answer.
        numUsers refers to the number of unique users that answered the question
        length is the total length of the article being annotated in characters
        dfunc is the distance function that should be used, ordinal or nominal
        output:
        This method returns the most chosen answer, all characters that were highlighted enough to pass the
        threshold matrix test, and reliability scores (between 0 and 1) for the coding and unitizing portions of the
        agreement score.  The variable 'iScore' refers to the unitizing agreement score calculated using Krippendorff's
        alpha including users who never highlighted any characters that passed the threshold matrix
    """
    repScaledAnswers, repScaledUsers = repScaleAnsUsers(answers, users)
    highScore, winner, weights = scoreCoding(repScaledAnswers, repScaledUsers, dfunc)
    if dfunc == 'ordinal':
        # This functions as an outlier test, if 4 users categorizes as 'very likely' and one categorizes as
        # 'very not likely', it will fail the threshold matrix test, this method, while not rigorous, provides
        # some defense against outliers that likely were produced by trolls, misunderstandings of the question,
        # and misclicks
        if evalThresholdMatrix(highScore, numUsers)!='H':
            highScore, winner, weights = scoreCoding(answers, users, 'nominal')
    # These all return tuples (array of answers, amount of scaling done), element at index 1 is same for all
    weightScaledAnswers, weightScaledUsers, weightScaledStarts, \
                                            weightScaledEnds, \
                                            weightScaledNumUsers = weightScaleEverything(answers, weights, users,
                                                                                         starts,ends)
    winner, units, uScore, iScore = passToUnitizing(weightScaledAnswers,weightScaledUsers,weightScaledStarts,
                                                    weightScaledEnds,numUsers,length, highScore, winner,
                                                    weightScaledNumUsers)
    return winner, units, uScore, iScore, highScore

def repScaleAnsUsers(answers, users):
    repScaledAnswers, repScaledUsers = scaleFromRep(answers, users), scaleFromRep(users, users)
    return repScaledAnswers, repScaledUsers

def weightScaleEverything(answers,weights, users, starts, ends):
    weightScaledAnswers, weightScaledStarts, weightScaledEnds, \
    weightScaledUsers = scaleFromWeights(answers, answers, weights, users), \
                        scaleFromWeights(starts, answers, weights, users), \
                        scaleFromWeights(ends, answers, weights, users), \
                        scaleFromWeights(users, answers, weights, users),
    ans, ends, starts, users = weightScaledAnswers[0], weightScaledEnds[0], weightScaledStarts[0], weightScaledUsers[0]
    numUsers = weightScaledUsers[1]
    return ans, users, starts, ends, numUsers

def passToUnitizing(answers,users,starts,ends,numUsers,length,\
    highScore, winner, scaledNumUsers):
    """ calculates unitizing agreement for any coding question after verifying that it passes the threshold matrix
    Only calculates unitizing agreement amongst users who selected the most agreed-upon answer"""
    if evalThresholdMatrix(highScore, numUsers) == 'H':
        goodIndices = filterIndexByAnswer(winner, answers)
        #f for filtered
        starts,ends, users = np.array(starts), np.array(ends), np.array(users)
        #fStarts, fEnds, fUsers = starts[goodIndices], ends[goodIndices], users[goodIndices]
        fStarts, fEnds, fUsers = starts, ends, users
        #fNumUsers = len(np.unique(fUsers))
        fNumUsers = scaledNumUsers
        #If somebody highlights something
        if max(fEnds)>0:
            uScore, iScore, units = scoreNuUnitizing(fStarts, fEnds, length, fNumUsers, fUsers, winner, answers)
        else:
            uScore = 'NA'
            iScore = 'NA'
            units = []
        return winner, units, uScore, iScore
    else:
        status = evalThresholdMatrix(highScore, numUsers)
        return status, status, status, status


def scoreCoding(answers, users, dfunc):
    """scores coding questions using an ordinal distance
    function(defined in getWinners method)
    inputs:
    answers array like object of the answers for the question
    users is array-like object of users that answered
    dfunc should be 'ordinal' or 'nominal', defaults to nominal
        answers and users should be the same length
    outputs:
    highest score any answer earned,
    the answer chosen most often
    a list containing userIds of users who chose that answer
    """
    answers = [int(a) for a in answers]
    if dfunc == 'ordinal':
        highscore, winner, weights = getWinnersOrdinal(answers)
    else:
        highscore, winner, weights = getWinnersNominal(answers)
    return highscore, winner, weights

def getWinnersOrdinal(answers, num_choices = 5):
    # Todo:confirm that I said the right thing about Shannon
    """Calculates the most-common answer and assigns it an agreement score
    uses Jensen-Shannon Distance to assign weights to different answers"""
    # Shannon Entropy ordinal metric
    # Todo: get number of possible answers as an input so we don't have to assume it's 5
    length = num_choices
    # index 1 refers to answer 1, 0 and the last item are not answer choices, but
    # deal with corner cases that would cause errors
    original_arr = np.array(answers) - 1
    aggregate_arr = np.zeros(length)
    for i in original_arr:
        aggregate_arr[i] += 1
    topScore, winner, weights = shannon_ordinal_metric(original_arr, aggregate_arr)
    # shift array so indexes consistent across ordinal and nominal data
    weights = np.append(0, weights)
    return topScore, winner + 1, weights

def shannon_ordinal_metric(original_arr, aggregate_arr):
    """"calculates Jensen-Shannon Metric """
    original_arr = np.array(original_arr)
    aggregate_arr = np.array(aggregate_arr)
    prob_arr = aggregate_arr / sum(aggregate_arr)
    x_mean = np.mean(original_arr)
    total_dist = len(aggregate_arr)
    score = 1 + np.dot(prob_arr, np.log2(1 - abs(np.arange(total_dist) - x_mean) / total_dist))
    winner = np.where(aggregate_arr == aggregate_arr.max())[0][0]
    weights= 1+np.log2(1 - abs(np.arange(total_dist) - x_mean) / total_dist)
    print(aggregate_arr)
    print(prob_arr)
    print(1+(np.log2(1 - abs(np.arange(total_dist) - x_mean) / total_dist)))
    return score, winner, weights

def getWinnersNominal(answers, num_choices = 5):
    """returns the most-chosen answer and the percentage of users that chose that answer"""
    length = num_choices+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
    winner = np.where(scores == scores.max())[0][0]
    topScore = scores[winner]/(len(answers))
    weights = np.zeros(length)
    weights[winner] = 1
    return topScore, winner, weights

def scaleFromRep(arr, users):
    """Scales the array based on user reps"""
    scaled = np.zeros(0)
    checked = []
    for i in range(len(arr)):
        if (arr[i], users[i]) not in checked:
            checked.append((arr[i], users[i]))
            addition = np.array(arr[i])
            rep = floor(get_user_rep(users[i]))
            addition = np.repeat(addition, rep)
            scaled = np.append(scaled, addition)
    return scaled

def scaleFromWeights(arr,answers,weights, users):
    """Scales the array based on the weights and the user reps"""
    #weights is array of fractions now
    weights = weights
    scaled = np.zeros(0)
    sumTotalScaling = 0
    checked = []
    for i in range(len(arr)):
        if (arr[i], users[i]) not in checked:
            checked.append((arr[i], users[i]))
            addition = np.array(arr[i])
            rep = get_user_rep(users[i])
            ans = answers[i]
            weight = weights[ans]
            scaleBy = floor(weight*rep)
            sumTotalScaling += scaleBy
            addition = np.repeat(addition, scaleBy)
            scaled = np.append(scaled, addition)
    return scaled.astype(int), sumTotalScaling
