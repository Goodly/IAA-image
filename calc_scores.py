import os
import argparse
import csv
#import pandas as pd
import numpy as np
from itertools import groupby
from collections import defaultdict

from jnius import autoclass
CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')

def read_csvfile(filename):
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        return collect_rows(reader)

def or_use_pandas(filename):
    df = pd.read_csv(filename)
    print(df.columns)
    print(df.groupby(['topic_number', 'question_number', 'contributor_id'])['contributor_id'].count())
    return df

def genStudies():
    st1 = CAS(5)
    st1.addItemAsArray(['1','1','1','1','1'])
    st2 = CAS(5)
    st2.addItemAsArray(['1','1','1','1','2'])
    st3 = CAS(5)
    st3.addItemAsArray(['1','2','3','4','5'])
    st4 = CAS(5)
    st4.addItemAsArray(['1','1','1','1','4'])
    return st1, st2, st3
#returns dictionary of dictoinaries--to access specifics:
#collect_rows(reader)[article_num][user][question] --> [answer_num, start_pos, end_pos]
#All inputs are strings
def collect_rows(reader):
    rows = [ row for row in reader ]
    sort_questions = lambda x: (x['topic_number'], x['question_number'], x['contributor_id'])
    anno_by_question = sorted(rows, key=sort_questions)
    ordinal_questions = ['2','3','4','5','6','13','14','15','16','17','18','19','20','21','25']
    nominal_questions = ['7','22']
    interval_questions = ['9','10','11']
    uberDict = {} # the most dictionarial dictionary
    for (topic_number, question_number, contributor_id), anno \
        in groupby(anno_by_question, key=sort_questions):
        #print(topic_number, question_number)
        #anno is a list of lists
        for row in anno:
            article_num = row['taskrun_article_number']
            if not article_num in uberDict:
                uberDict[article_num] = {}
            question = row['question_number']
            user = row['contributor_id']
            if not question in uberDict[article_num]:
                uberDict[article_num][question] = {}

            # if question in uberDict[article_num][user]:
            #     print("*****%^$^$^% SOMETHING WRONG, SAME Q \
            #     READ TWICE FROM SAME USER AND ARTICLE")
            answer = row['answer_number']
            start = row['start_pos']
            end = row['end_pos']
            uberDict[article_num][question][user] = [answer, start, end]

            # build a useful data structure here
    return uberDict

#returns dictionary of dictoinaries--to access specifics:
#collect_rows(reader)[article_num][user][question] --> [answer_num, start_pos, end_pos]
#All inputs are strings
def collect_rows_old(reader):
    rows = [ row for row in reader ]
    sort_questions = lambda x: (x['topic_number'], x['question_number'], x['contributor_id'])
    anno_by_question = sorted(rows, key=sort_questions)
    ordinal_questions = ['2','3','4','5','6','13','14','15','16','17','18','19','20','21','25']
    nominal_questions = ['7','22']
    interval_questions = ['9','10','11']
    uberDict = {} # the most dictionarial dictionary
    for (topic_number, question_number, contributor_id), anno \
        in groupby(anno_by_question, key=sort_questions):
        #print(topic_number, question_number)
        #anno is a list of lists
        for row in anno:
            article_num = row['taskrun_article_number']
            if not article_num in uberDict:
                uberDict[article_num] = {}
            user = row['contributor_id']
            if not user in uberDict[article_num]:
                uberDict[article_num][user] = {}
            question = row['question_number']
            # if question in uberDict[article_num][user]:
            #     print("*****%^$^$^% SOMETHING WRONG, SAME Q \
            #     READ TWICE FROM SAME USER AND ARTICLE")
            answer = row['answer_number']
            start = row['start_pos']
            end = row['end_pos']
            uberDict[article_num][user][question] = [answer, start, end]

            # build a useful data structure here
    return uberDict

#collect_rows(reader)[article_num][user][question] --> [answer_num, start_pos, end_pos]
#toStudies(data)[article][question]->Study
def toStudies(data):
    articKeys = data.keys()
    uberStudyDict = {}
    for article in articKeys:
        articdata = data[article]
        users = articdata.keys()
        questionsAnswered = []
        uberStudyDict[article] = {}
        for user in users:
            userarticdata = articdata[user]
            questionsThisUserAnswered = articdata[user].keys()
            for q in questionsThisUserAnswered:
                if not q in questionsAnswered:
                    questionsAnswered.append(q)

        for quest in questionsAnswered:
            featuredInThisStudy = []
            for u  in users:
                questionsThisUserAnswered = articdata[user].keys()
                if quest in questionsThisUserAnswered:
                    featuredInThisStudy.append(articdata[user][quest][0])
            numContributors = len(featuredInThisStudy)
            study = CAS(numContributors)
            study.addItemAsArray(featuredInThisStudy)
            uberStudyDict[article][quest] = study
    return uberStudyDict

#Takes the uberDict from the collect_rows method as input
#toKrypp(data)[article][question][OBservedDisagreement, expectedDisagreement, α coefficient, Categtory 1 α, Categtory 2 α]
def toKrypp(data):
    articKeys = data.keys()
    uberStudyDict = {}
    for article in articKeys:
        articdata = data[article]
        users = articdata.keys()
        questionsAnswered = []
        uberStudyDict[article] = {}
        for user in users:
            userarticdata = articdata[user]
            questionsThisUserAnswered = articdata[user].keys()
            for q in questionsThisUserAnswered:
                if not q in questionsAnswered:
                    questionsAnswered.append(q)

        for quest in questionsAnswered:
            featuredInThisStudy = []
            for u  in users:
                questionsThisUserAnswered = articdata[user].keys()
                if quest in questionsThisUserAnswered:
                    featuredInThisStudy.append(articdata[user][quest][0])
            numContributors = len(featuredInThisStudy)
            print(numContributors)
            study = CAS(numContributors)
            print(study)
            alpha = KAA(study, NDF())
            observed = alpha.calculateObservedDisagreement()
            expected = alpha.calculateExpectedDisagreement()
            alphCoef = alpha.calculateAgreement()
            cat1Coef = alpha.calculateCategoryAgreement("1")
            cat2Coef = alpha.calculateCategoryAgreement("2")
            out = [observed, expected, alphCoef,cat1Coef,cat2Coef]
            uberStudyDict[article][quest] = out
    return uberStudyDict







def get_csv_reader(filename):
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        print(type(reader))
        return reader



def calculate_scores(data):
    scores = []
    return scores

def write_scores_csv(scores):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--input-file',
        help='CSV file with TextThresher Data Hunt columns.')
    args = parser.parse_args()
    filename = "./pe_data/pe_users_13_14_15-2018-03-19T18.csv"
    if args.input_file:
        filename = args.input_file
    data = read_csvfile(filename)
    #data = or_use_pandas(filename)
    #scores = calculate_scores(data)
    #write_scores_csv(scores)
