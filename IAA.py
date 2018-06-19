import pandas as pd
import numpy as np
from jnius import autoclass
import csv
from UnitizingScoring import *
from IAA_unitizing_PA import *

def run_2step_unitization(data, article, question):
        starts,ends,length,numUsers, users = get_question_start(data,article,question).tolist(),get_question_end(data,article,question).tolist(),\
                        get_text_length(data,article,question), get_num_users(data,article,question),  get_question_userid(data, article, question).tolist()
        score = scoreNickUnitizing(starts,ends,length,numUsers, users)
        return score
