
# coding: utf-8

# In[2]:


from datascience import *
import numpy as np


# In[3]:


table = Table.read_table("./SSS_pull_8_22/S_IAA_SSSPECaus2-2018-08-22T2019-DataHuntHighlights.csv")
table
data = table.where("agreed_Answer", are.not_contained_in('ULM'))
data.show()


# In[ ]:


def weighted_q6(num):
    if num >= 160:
        score = 0
    elif 150 <= num < 160:
        score = 0.5
    elif 100 <= num <150:
        score = 2
    elif 50 <= num <100:
        score = 3
    elif num < 50:
        score = 4
    else:
        score = 5
    return score


# In[9]:


minus = 0
q6_num = 0

a = "Correlation"
b = "Cause precedes effect"
c = "The correlation appears across multiple independent contexts"
d = "A plausible mechanism is proposed"
e = "An experimental study was conducted (natural experiments OK)"
f = "The bigger the cause, the bigger the effect (dose response curve)"
g = "Experts are cited"
h = "Other evidence"
i = "No evidence given"

for row in data.rows:
    if row.item("question_Number") == 1:
        minus += 0.2 * row.item("agreed_Answer") * row.item("agreement_score")
    if row.item("question_Number") == 6:
        if row.item("answer_content") == a or row.item("answer_content") == b or row.item("answer_content") == d:
            q6_num += row.item("agreement_score") * 50
        if row.item("answer_content") == c or row.item("answer_content") == e or row.item("answer_content") == f:
            q6_num += row.item("agreement_score") * 10
        if row.item("answer_content") == g or row.item("answer_content") == h:
            q6_num += row.item("agreement_score") * 1
            
credibility = 99 - (minus + weighted_q6(q6_num))
credibility

