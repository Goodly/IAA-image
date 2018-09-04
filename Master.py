from IAA import *
from Dependency import *
from Weighting import *
from pointAssignment import *
from Separator import *
def calculate_scores_master(directory, tua = 'allTUAS.csv'):
    print("IAA PROPER")
    calc_agreement_directory(directory, hardCodedTypes=True)
    print("DEPENDENCY")
    eval_depenency(directory)
    print("WEIGHTING")
    launch_Weighting(directory)
    print("SORTING POINTS")
    pointSort(directory)
    print("----------------SPLITTING-----------------------------------")
    splitcsv(directory)

calculate_scores_master('pred1')