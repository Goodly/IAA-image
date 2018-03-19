import os
import argparse
import csv
import pandas as pd

def load_metadata(reader):
    for row in reader:
        print(row['topic_number'], row['question_number'])

def read_csvfile(filename):
    with open(filename, encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        load_metadata(reader)

def or_use_pandas(filename):
    df = pd.read_csv(filename)
    print(df.columns)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--input-file',
        help='CSV file with TextThresher Data Hunt columns.')
    args = parser.parse_args()
    filename = "./pe_data/pe_users_13_14_15-2018-03-19T18.csv"
    if args.input_file:
        filename = args.input_file
    read_csvfile(filename)
    or_use_pandas(filename)
