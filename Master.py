import argparse

from IAA import *
from Dependency import *
from Weighting import *
from pointAssignment import *
from Separator import *
def calculate_scores_master(directory):
    print("IAA PROPER")
    calc_agreement_directory(directory, hardCodedTypes=True, repCSV="UserRepScores.csv")
    print("DEPENDENCY")
    eval_depenency(directory)
    print("WEIGHTING")
    launch_Weighting(directory)
    print("SORTING POINTS")
    pointSort(directory)
    print("----------------SPLITTING-----------------------------------")
    splitcsv(directory)

def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-dir',
        help='Directory containing DataHuntHighlights DataHuntAnswers, '
             'and Schema .csv files.')
    parser.add_argument(
        '-o', '--output-dir',
        help='Pathname to use for output file.')
    return parser.parse_args()

if __name__ == '__main__':
    args = load_args()
    input_dir = 'pred1'
    if args.input_dir:
        input_dir = args.input_dir
    calculate_scores_master(input_dir)
