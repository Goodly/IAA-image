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
ODF = autoclass('org.dkpro.statistics.agreement.distance.OrdinalDistanceFunction')

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

    return st1, st2, st3,st4
