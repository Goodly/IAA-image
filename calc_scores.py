import os
import argparse
import csv
import pandas as pd
from itertools import groupby
from collections import defaultdict

def read_csvfile(filename):
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        return collect_rows(reader)

def collect_rows(reader):
    rows = [ row for row in reader ]
    sort_questions = lambda x: (x['topic_number'], x['question_number'], x['contributor_id'])
    anno_by_question = sorted(rows, key=sort_questions)
    for (topic_number, question_number, contributor_id), anno \
        in groupby(anno_by_question, key=sort_questions):
        print(topic_number, question_number)
        for row in anno:
            print(row['contributor_id'], row['answer_number'], row['answer_text'])
            # build a useful data structure here
    # return data

def or_use_pandas(filename):
    df = pd.read_csv(filename)
    print(df.columns)
    grouped = df.groupby(['topic_number', 'question_number', 'contributor_id'])
    print(grouped['contributor_id'].count())
    for (topic_number, question_number, contributor_id), group in grouped:
        print("--------------")
        print((topic_number, question_number, contributor_id))
        print(group[['answer_number', 'answer_text']])
            # build a useful data structure here
    # return data

def calculate_scores(data):
    scores =[]
    return scores

def write_scores_csv(output_filename, scores):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--input-file',
        help='CSV file with TextThresher Data Hunt columns.')
    args = parser.parse_args()
    filename = "./pe_data/pe_users_13_14_15-2018-03-19T18.csv"
    output_filename = "./pe_data/someresults.csv"
    if args.input_file:
        filename = args.input_file
    data1 = read_csvfile(filename)
    data2 = or_use_pandas(filename)
    scores = calculate_scores(data1)
    write_scores_csv(output_filename, scores)
