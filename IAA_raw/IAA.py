import csv
from ChecklistCoding import *
from data_utils import *

path = './test/TestJuntos.csv'


def calc_scores(filename):
    uberDict = data_storer(filename)
    data = [["Article Number", "Question Number", "Agreed Answer", "Coding Score", "HighlightedIndices",\
             "Alpha Unitizing Score", "Alpha Unitizing Score Inclusive", "Agreement Score"]]

    for article in uberDict.keys(): #Iterates throuh each article
        for ques in uberDict[article].keys(): #Iterates through each question in an article
            agreements = score(article, ques, uberDict)
            #if it's a list then it was a checklist question
            if type(agreements) is list:
                for i in range(len(agreements)):
                    codingScore, unitizingScore = agreements[i][4], agreements[i][2]
                    totalScore = calcAgreement(codingScore, unitizingScore)
                    data.append([article, ques, agreements[i][0], codingScore, agreements[i][1],
                                 unitizingScore, agreements[i][3], totalScore])
            else:
                codingScore, unitizingScore = agreements[4], agreements[2]
                totalScore = calcAgreement(codingScore, unitizingScore)
                data.append([article,ques, agreements[0], codingScore, agreements[1], unitizingScore, agreements[3],
                             totalScore])
    #push out of womb, into world
    print('exporting to csv')
    scores = open('agreement_scores.csv', 'w')

    with scores:
        writer = csv.writer(scores)
        writer.writerows(data)

    print("Table complete")

def score(article, ques, data):
    """calculates the relevant scores for the article
    returns a tuple (question answer most chosen, units passing the threshold,
        the Unitizing Score of the users who highlighted something that passed threshold, the unitizing score
        among all users who coded the question the same way (referred to as the inclusive unitizing score),
         the percentage agreement of the category with the highest percentage agreement """

    """ Commnted code below previously denoted different types of questions for hard-coding,
    can still be used for hard-coding but eventually will be phased out by a line of code that
    checks the type based off the table data"""
    # ordinal_questions = [1,2,4,12,13,14,15,16,17,18,19,20,21,25]
    # nominal_questions = [7,22]
    # unit_questions = [9,10,11, 24] #asks users to highlight, nothing else OR they highlight w/ txt answer
    # multiple_questions = [3,5,8,23]

    print('Scoring article: ', article, ' question: ', ques)
    type = get_question_type(data,article, ques)
    if type == 'interval':
        return run_2step_unitization(data, article, ques)

    answers, users,  numUsers = get_question_answers(data, article, ques).tolist(), \
        get_question_userid(data, article, ques).tolist(), \
        get_num_users(data, article, ques)
    starts,ends,length= get_question_start(data,article,ques).tolist(),get_question_end(data,article,ques).tolist(),\
                        get_text_length(data,article,ques)
    if type == 'ordinal':
        return evaluateCoding(answers, users, starts, ends, numUsers, length, dfunc = 'ordinal')
    elif type == 'nominal':
        return evaluateCoding(answers, users, starts, ends, numUsers, length)
    elif type == 'checklist':
        return evaluateChecklist(answers, users, starts, ends, numUsers, length)

def calcAgreement(codingScore, unitizingScore):
    """averages coding and unitizing agreement scores to create a final agreement score to be used elsewhere in the
    Public Editor algorithm"""
    if codingScore == 'NA':
        return unitizingScore
    elif codingScore == 'L' or codingScore == 'M':
        return codingScore
    elif unitizingScore == 'NA':
        return codingScore
    elif unitizingScore == 'L' or unitizingScore == 'M':
        unitizingScore = 0

    return (float(codingScore)+float(unitizingScore))/2

#TODO: make this return a tuple with agreed upon answer as first statement and agreed upon score as second
def run_2step_unitization(data, article, question):
        starts,ends,length,numUsers, users = get_question_start(data,article,question).tolist(),get_question_end(data,article,question).tolist(),\
                        get_text_length(data,article,question), get_num_users(data,article,question),  get_question_userid(data, article, question).tolist()
        uqU = np.unique(users)
        userWeightDict = {}
        for u in uqU:
            userWeightDict[u] = get_user_rep(u)
        score, indices, iScore = scoreNuUnitizing(starts,ends,length,numUsers, users, userWeightDict)
        return 'NA',  indices, score, score, 'NA'

#TEST STUFF
calc_scores(path)