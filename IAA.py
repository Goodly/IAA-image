import pandas as pd
import numpy as np
from jnius import autoclass
import csv
from UnitizingScoring import *
from IAA_unitizing_PA import *

def calc_scores(filename):
    uberDict = data_storer(filename)
    data = [["Article Number", "Question Number", "Agreed Answer", "Agreement Score"]]

    for article in uberDict.keys(): #Iterates thrguh each article
        for ques in uberDict[article].keys(): #Iterates through each question in an article
            agreements = score(article, ques, uberDict)
            data.append([article,ques, agreements[0], agreements[1]])
    #@TODO return the csv, or make sure it's pushed out of the womb and into the world

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
    # ordinal_questions =
    # nominal_questions =
    # unit_questions =
    # multiple_questions =

    print('Scoring article: ', article, ' question: ', ques)

    #TODO: change this to be not hard-coded
    if ques in unit_questions:
        return run_2step_unitization(data, article, ques)


    if ques in ordinal_questions:
        #TODO: put ordinal score calculation here
        return ...
    elif ques in nominal_questions:
        #TODO: put nominal score calculation here
        return ...
    elif ques in multiple_questions:
        #TODO: put multiple question scoring here
        #I believe we should just loop through and do each once nominally but for syntax sake we can make a seperate function
        return ...







#TODO: make this return a tuple with agreed upon answer as first statement and agreed upon score as second
def run_2step_unitization(data, article, question):
        starts,ends,length,numUsers, users = get_question_start(data,article,question).tolist(),get_question_end(data,article,question).tolist(),\
                        get_text_length(data,article,question), get_num_users(data,article,question),  get_question_userid(data, article, question).tolist()
        score = scoreNickUnitizing(starts,ends,length,numUsers, users)
        return score
