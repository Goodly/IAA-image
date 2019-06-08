import argparse

from IAA import calc_agreement_directory
from Dependency import *
from Weighting import *
from pointAssignment import *
from Separator import *


def calculate_scores_master(directory, tua_file = None, iaa_dir = None, scoring_dir = None, repCSV = None):
    """

    :param directory: the directory that holds all files from the tagworks datahunt export
    :param tua_file: directory to the file holding all the TUAs that created the datahunt tasks
    :param iaa_dir: the directory to output the raw IAA data to; if no input default is s_iaa_<directory>
    :param scoring_dir: directory to output data from every other stage of the scoring algorithm to; if no
        input default is scoring_<directory>
    :param repCSV: the csv that holds the rep score data
    :return: No explicit return.  Running will create two directories named by the inputs. the iaa_dir will house
        a csv output from the IAA algorithm.  The scoring_dir will house the csvs output from the dependency evaluation
        algorithm; the weighting algorithm; the point sorting algorithm; and the final cleaning algorithm that prepares
        data to be visualized
    """
    print("IAA PROPER")
    iaa_dir = calc_agreement_directory(directory, hardCodedTypes=True, repCSV=repCSV, outDirectory=iaa_dir)
    print('iaaaa', iaa_dir)
    print("DEPENDENCY")
    scoring_dir = eval_dependency(directory, iaa_dir, out_dir=scoring_dir)
    print("WEIGHTING")
    launch_Weighting(scoring_dir)
    print("SORTING POINTS")
    pointSort(scoring_dir, tua_file)
    print("----------------SPLITTING-----------------------------------")
    splitcsv(scoring_dir)

def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-dir',
        help='Directory containing DataHuntHighlights DataHuntAnswers, '
             'and Schema .csv files.')
    parser.add_argument(
        '-t', '--tua-file',
        help='Filename to use for file with TUAs for taskruns in input-dir.')
    parser.add_argument(
        '-o', '--output-dir',
        help='Pathname to use for IAA output directory.')
    parser.add_argument(
        '-s', '--scoring-dir',
        help='Pathname to use for output files for scoring of articles.')
    parser.add_argument(
        '-r', '--rep-file',
        help='Filename to use for User Reputation scores file.')
    return parser.parse_args()

if __name__ == '__main__':
    args = load_args()
    input_dir = 'langdeptest'
    tua_file = './mt/allTUAS.csv'
    output_dir = None
    scoring_dir  = None
    rep_file = './UserRepScores.csv'
    if args.input_dir:
        input_dir = args.input_dir
    if args.tua_file:
        tua_file = args.tua_file
    if args.output_dir:
        output_dir = args.output_dir
    if args.scoring_dir:
        scoring_dir = args.scoring_dir
    if args.rep_file:
        rep_file = args.rep_file
    calculate_scores_master(input_dir, tua_file=tua_file, iaa_dir=output_dir, scoring_dir=scoring_dir, repCSV=rep_file)

#calculate_scores_master("urap")