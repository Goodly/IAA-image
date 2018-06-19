import pandas as pd
import numpy as np
from jnius import autoclass
import csv
from UnitizingScoring import *
from IAA_unitizing_PA import *

def run_2step_unitization(data, article, question):
    user_ans_dict = get_user_arrays(data,article, question)
    q_ratios = get_question_answer_ratios(user_ans_dict)
