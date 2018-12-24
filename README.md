
Steps to run Inter-Annotator Agreement on Highlighter.

1. virtualenv --python=python3 ../iaa.env
2. ../iaa.env/bin/activate
3. pip install -r requirements.txt
4. cd SemanticsTriager1.4C2/
4. python3 TriagerScoring.py -i SemanticsTriager1.4C2-2018-10-31T2311-Highlighter.csv


Output file is in current directory, prefixed with T_
