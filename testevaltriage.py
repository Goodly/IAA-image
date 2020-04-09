from pointAssignment import pointSort
from holistic_eval import eval_triage_scoring


tuas, weights, tua_raw = pointSort('scoring_covid', 'covid/')
eval_triage_scoring(tua_raw, weights, 'covid/', 'scoring_covid',)