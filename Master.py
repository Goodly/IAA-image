from IAA import calc_agreement_directory
from Dependency import eval_depenency
from Weighting import launch_Weighting
from pointAssignment import pointSort
from Separator import splitcsv
def calculate_scores(directory, tua = 'allTUAS.csv'):
    calc_agreement_directory(directory, hardCodedTypes=True)
    eval_depenency(directory)
    launch_Weighting(directory)
    pointSort(directory)
    splitcsv(directory)

calculate_scores('pred1')