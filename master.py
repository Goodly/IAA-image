import argparse

from IAA import calc_agreement_directory
from IAA import calc_scores
from Dependency import *
from Weighting import *
from pointAssignment import *
from Separator import *
from IAA_report import make_iaa_human_readable
from dataV2 import make_directory
from time import time
from send_to_s3 import send_s3
from GenerateVisualization import visualize
from eval_overalls import eval_triage_scoring
from art_to_id_key import make_key

def calculate_scores_master(directory, tua_file = None, iaa_dir = None, scoring_dir = None, repCSV = None,
                            just_s_iaa = False, just_dep_iaa = False, use_rep = False, reporting  = True,
                            single_task = False, highlights_file = None, schema_file = None, answers_file = None,
                            push_aws = True, out_prefix = '', threshold_func = 'logis_0'):
    """

    :param directory: the directory that holds all files from the tagworks datahunt export
    :param tua_file: directory to the file holding all the TUAs that created the datahunt tasks
    :param iaa_dir: the directory to output the raw IAA data to; if no input default is s_iaa_<directory>
    :param scoring_dir: directory to output data from every other stage of the scoring algorithm to; if no
        input default is scoring_<directory>
    :param repCSV: the csv that holds the rep score data
    :param just_s_iaa: True if the calculations should stop after the initial specialist IAA computation, false otherwise
    :param just_dep_iaa: True if the calculations should stop after the initial specialist IAA computation and the
        dependency computation, false otherwise
    :param use_rep: True if the scores should be computed using user rep scores; false otherwise
    :param reporting: True if user would like extra csv outputs.  These csvs aren't necessary to score but may be useful
        to humans trying to understand and analyze the algorithms
    :param single_task: True if there's only one task to be analyzed, false otherwise
    :param: highlights_file: only used if single_task is true; necessary if single_task is true; the path to the
        highlights file that is output from tagworks
    :param: schema_file: only used if single_task is true; necessary if single_task is true; the path to the schema file
        that is output from tagworks
    :param anwers_file: only used if single_task is true; necessary if single_task is true; the path to the answers file
        that is output from tagworks
    **if in the future the data import is adjusted to depend on other file outputs from tagworks, new parameters would
        have to be added to accomodate the change in importing procedures
    :param push_aws: True if we want outputs sent to the s3 AWS folder, false to just store locally
    :param out_prefix: add something to the prefix of output files to keep everything tidy
    :param: threshold_func: the threshold function being used to determine inter-annotator agreement; for a
        comprehensive test of all the threshold functions set this to 'all'; this will not work if an iaa_directory is
        specified
    :return: No explicit return.  Running will create two directories named by the inputs. the iaa_dir will house
        a csv output from the IAA algorithm.  The scoring_dir will house the csvs output from the dependency evaluation
        algorithm; the weighting algorithm; the point sorting algorithm; and the final cleaning algorithm that prepares
        data to be visualized
    """
    print(threshold_func)
    all_funcs = ['raw_70', 'raw_50', 'raw_30', 'logis_0', 'logis+20', 'logis+40']
    target_funcs = ['raw_70', 'raw_50', 'raw_30']
    #all_funcs is every possible scoring function; target_funcs is just the functions you want to test when you say all
    if threshold_func == 'all':
        for func in target_funcs:
            if iaa_dir is None:
                if directory.startswith('./'):
                    iaa_direc = 's_iaa_' + func + '_' + directory[2:]
                else:
                    iaa_direc = 's_iaa_' + func + '_' + directory
            if scoring_dir is None:
                if directory.startswith('./'):
                    scoring_direc = 'scoring_' + func + '_' + directory[2:]
                else:
                    scoring_direc = 'scoring_' + func + '_' + directory
            calculate_scores_master(directory, tua_file=tua_file, iaa_dir=iaa_direc, scoring_dir=scoring_direc,
                                    repCSV=repCSV, just_s_iaa=just_s_iaa, just_dep_iaa=just_dep_iaa, use_rep=use_rep,
                                    reporting=reporting,single_task=single_task, highlights_file=highlights_file,
                                    schema_file=schema_file, answers_file=answers_file,
                                    push_aws=push_aws, out_prefix=out_prefix, threshold_func=func)
        return

    print("IAA PROPER")
    #iaa_dir is now handled inside IAA.py
    #if iaa_dir is None:
    #    iaa_dir = 's_iaa_'+directory
    print("PUSH AWS VAL", push_aws)
    print("PREFFF", out_prefix)
    rep_direc = directory + "_report"
    make_directory(rep_direc)
    start = time()
    if not single_task:
        iaa_dir = calc_agreement_directory(directory, hardCodedTypes=True, repCSV=repCSV, outDirectory=iaa_dir,
                                           useRep=use_rep, threshold_func=threshold_func)
    else:

        iaa_dir = calc_scores(highlights_file, repCSV=repCSV, answersFile = answers_file, schemaFile = schema_file,
                              outDirectory = iaa_dir, useRep = use_rep, threshold_func=threshold_func)

    if reporting:
        make_iaa_human_readable(iaa_dir, rep_direc)
    if just_s_iaa:
        return
    end = time()
    print("IAA TIME ELAPSED", end - start)
    print('iaaaa', iaa_dir)
    print("DEPENDENCY")
    scoring_dir = eval_dependency(directory, iaa_dir, out_dir=scoring_dir)
    if just_dep_iaa:
        return

    print("WEIGHTING")
    launch_Weighting(scoring_dir)
    print("SORTING POINTS")
    tuas, weights = pointSort(scoring_dir, directory)

    eval_triage_scoring(tuas, weights, scoring_dir)
    make_key(tuas, scoring_dir, out_prefix)
    print("----------------SPLITTING-----------------------------------")
    splitcsv(scoring_dir)
    #print("DONE, time elapsed", time()-start)
    ids = []
    if push_aws:
        print("Pushing to aws")
        ids = send_s3(scoring_dir, directory, prefix=out_prefix, func = threshold_func)

    for id in ids:
        visualize(id, prefix=out_prefix)

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
        '-rf', '--rep-file',
        help='Filename to use for User Reputation scores file.')
    parser.add_argument(
        '-ji', '--just_s_iaa',
        help='True if you only wish to run the base IAA algorithm (agreement check, agreement score, '
             'krippendorff alpha unitization)')
    parser.add_argument(
        '-jd', '--just_d_iaa',
        help='True if you only wish to run the base IAA algorithm and the dependency handling algorithm(agreement check,'
             ' agreement score, krippendorff alpha unitization); Remove rows without agreement or without a passing '
             'parent question and apply unitizations to child questions')
    parser.add_argument(
        '-r', '--use_rep',
        help='True if we want to use reputation scores, false otherwise')
    parser.add_argument(
        '-st', '--single_task',
        help="True if there's only one task to be analyzed, false otherwise")
    parser.add_argument(
        '-hf', '--highlights_file',
        help="only used if single_task is true; necessary if single_task is true; the path to the highlights file that is output from tagworks")
    parser.add_argument(
        '-sf', '--schema_file',
        help="only used if single_task is true; necessary if single_task is true; the path to the schema file that is output from tagworks")
    parser.add_argument(
        '-af', '--answers_file',
        help="only used if single_task is true; necessary if single_task is true; the path to the answers file that is output from tagworks")
    parser.add_argument(
        '-p', '--push_aws',
        help= "true if you want to push the visualization data to the aws s3; false by default")
    parser.add_argument(
        '-pre', '--out_prefix',
        help='optional, if you need a prefix before the visualization data for testing, make this variable not be a zero string')
    parser.add_argument(
        '-tf', '--threshold_function',
        help= 'the threshold function used to check for inter annotator agreement'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = load_args()
    input_dir = 'nyu_3_4'
    tua_file = './config/allTUAS.csv'
    output_dir = None
    scoring_dir  = None
    rep_file = './UserRepScores.csv'
    out_prefix = ''
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
    if args.out_prefix:
        out_prefix = args.out_prefix
    if args.threshold_function:
        threshold_function = args.threshold_function

    calculate_scores_master(input_dir, tua_file=tua_file, iaa_dir=output_dir, scoring_dir=scoring_dir, repCSV=rep_file,
                            out_prefix = out_prefix, threshold_func=threshold_function)

#calculate_scores_master("nyu_0")