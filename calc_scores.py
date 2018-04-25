import os
import argparse
import csv
#import pandas as pd
import numpy as np
from itertools import groupby
from collections import defaultdict
from Integer import *

from jnius import autoclass

CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')

def read_csvfile(filename):
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        return collect_rows(reader)

# def or_use_pandas(filename):
#     df = pd.read_csv(filename)
#     print(df.columns)
#     print(df.groupby(['topic_number', 'question_number', 'contributor_id'])['contributor_id'].count())
#     return df

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
        print(topic_number, question_number)
        #anno is a list of lists
        for row in anno:
            article_num = row['taskrun_article_number']
            if not article_num in uberDict:
                uberDict[article_num] = {}
            user = row['contributor_id']
            if not user in uberDict[article_num]:
                uberDict[article_num][user] = {}
            question = row['question_number']
            if question in uberDict[article_num][user]:
                print("*****%^$^$^% SOMETHING WRONG, SAME Q \
                READ TWICE FROM SAME USER AND ARTICLE")
            answer = row['answer_number']
            start = row['start_pos']
            end = row['end_pos']
            uberDict[article_num][user][question] = [answer, start, end]

            # build a useful data structure here
    return uberDict

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
