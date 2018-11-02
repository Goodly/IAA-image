import argparse

from IAA import *
from Dependency import *
from Weighting import *
from pointAssignment import *
from Separator import *


def calculate_scores_master(directory, iaa_dir = None, scoring_dir = None):
    print("IAA PROPER")
    iaa_dir = calc_agreement_directory(directory, hardCodedTypes=True, repCSV="UserRepScores.csv", outDirectory=iaa_dir)
    print('iaaaa', iaa_dir)
    print("DEPENDENCY")
    scoring_dir = eval_dependency(directory, iaa_dir, out_dir=scoring_dir)
    print("WEIGHTING")
    launch_Weighting(scoring_dir)
    print("SORTING POINTS")
    pointSort(scoring_dir)
    print("----------------SPLITTING-----------------------------------")
    splitcsv(scoring_dir)

def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-dir',
        help='Directory containing DataHuntHighlights DataHuntAnswers, '
             'and Schema .csv files.')
    parser.add_argument(
        '-o', '--output-dir',
        help='Pathname to use for IAA output file.')
    parser.add_argument(
        '-s', '--scoring-dir',
        help='Pathname to use for output files for scoring of articles.')
    return parser.parse_args()

if __name__ == '__main__':
    args = load_args()
    input_dir = 'demo3'
    output_dir = 'd4iaa'
    scoring_dir  = 'd5scoring'
    if args.input_dir:
        input_dir = args.input_dir
        output_dir = args.output_dir
        scoring_dir = args.scoring_dir
    calculate_scores_master(input_dir, output_dir, scoring_dir)
