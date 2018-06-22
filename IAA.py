import pandas as pd
import numpy as np
import csv
from UnitizingScoring import *
from MultipleCoding import *
from data_utils import *

path = './pe_data/pe_users_13_14_15-2018-03-19T18.csv'


def calc_scores(filename):
    uberDict = data_storer(filename)
    data = [["Article Number", "Question Number", "Agreed Answer", "HighlightedIndices","Agreement Score"]]

    for article in uberDict.keys(): #Iterates thrguh each article
        for ques in uberDict[article].keys(): #Iterates through each question in an article
            agreements = score(article, ques, uberDict)
            #if it's a list then it was a multiple q
            if type(agreements) is list:
                for i in range(len(agreements)):
                    data.append([article, ques, agreements[i][0],agreements[i][1], agreements[i][2]])
            else:
                data.append([article,ques, agreements[0], agreements[1], agreements[2]])
    #@TODO return the csv, or make sure it's pushed out of the womb and into the world
    print('exporting to csv')
    scores = open('question_scores.csv', 'w')

    with scores:
        writer = csv.writer(scores)
        writer.writerows(data)

    print("Table complete")

def score(article, ques, data):
    """Call this to get what you want
    It'll check for different types of questionsAnswered
    ifit's an interval question it'll return a random number

    returns a tuple, element 0 is winning answer, element 1 is the disagreement score """



    """ Commnted code below previously denoted different types of questions for hard-coding,
    can still be used for hard-coding but eventually will be phased out by a line of code that
    checks the type based off the table data"""
    ordinal_questions = [1,2,4,12,13,14,15,16,17,18,19,20,21,25]
    nominal_questions = [7,22]
    unit_questions = [9,10,11, 24] #asks users to highlight, nothing else OR they highlight w/ txt answer
    multiple_questions = [3,5,8,23]

    print('Scoring article: ', article, ' question: ', ques)

    #TODO: change this to be not hard-coded
    if ques in unit_questions:
        return run_2step_unitization(data, article, ques)

    answers, users,  numUsers = get_question_answers(data, article, ques).tolist(), \
        get_question_userid(data, article, ques).tolist(), \
        get_num_users(data, article, ques)
    starts,ends,length= get_question_start(data,article,ques).tolist(),get_question_end(data,article,ques).tolist(),\
                        get_text_length(data,article,ques)
    if ques in ordinal_questions:
        #TODO: put ordinal score calculation here


        return evaluateCoding(answers, users, starts, ends, numUsers, length, dfunc = 'ordinal')
    elif ques in nominal_questions:
        #TODO: put nominal score calculation here
        return evaluateCoding(answers, users, starts, ends, numUsers, length)
    elif ques in multiple_questions:
        #TODO: put multiple question scoring here
        #I believe we should just loop through and do each once nominally but for syntax sake we can make a seperate function
        return evaluateMultiple(answers, users, starts, ends, numUsers, length)







#TODO: make this return a tuple with agreed upon answer as first statement and agreed upon score as second
def run_2step_unitization(data, article, question):
        starts,ends,length,numUsers, users = get_question_start(data,article,question).tolist(),get_question_end(data,article,question).tolist(),\
                        get_text_length(data,article,question), get_num_users(data,article,question),  get_question_userid(data, article, question).tolist()
        score, indices = scoreNickUnitizing(starts,ends,length,numUsers, users)
        return 'N/A', indices, score

#TEST STUFF
calc_scores(path)