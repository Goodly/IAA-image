from pointAssignment import pointSort
from eval_triage import eval_triage_scoring


tuas, weights = pointSort('scoring_nyu_6_lang', 'nyu_6_lang/')
eval_triage_scoring(tuas, weights, 'nyu_6_lang/')