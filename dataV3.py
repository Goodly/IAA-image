import pandas as pd
import numpy as np

data_hunt_path = "nyu_reconfig/NYU_Arguments-2020-02-24T0112-DataHunt.csv"
def testDataStorer():
    # explore(data_hunt_path)
    uberDict = dataStorer(data_hunt_path)
    firstKey = list(uberDict.keys())[0]
    print()
    print(uberDict[firstKey])

def explore(data_hunt_path):
    data_hunt = pd.read_csv(data_hunt_path, encoding='utf-8')
    task_questions = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "answer_label"]]
    print(task_questions[task_questions["quiz_task_uuid"] == task_questions["quiz_task_uuid"].loc[0]])


def dataStorer(data_hunt_path):
    """
    Takes in the csv file path and turns csv into a dictionary
    """
    data_hunt = pd.read_csv(data_hunt_path, encoding = 'utf-8')
    uberDict = {}

    # Creates multiple smaller tables for data access
    task_article = data_hunt.loc[:,["quiz_task_uuid", "article_batch_name", "article_number",
                                    "article_filename", "article_sha256", "article_text_length"
                                    ]].drop_duplicates().set_index("quiz_task_uuid")
    task_id_url_data = data_hunt.loc[:, ["quiz_task_uuid", "task_url", "tua_uuid"]].drop_duplicates()

    task_questions_labels = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "answer_label"]]
    taskrun_task = data_hunt.loc[:, ["quiz_task_uuid", "taskrun_count", "quiz_taskrun_uuid",
                                     "created", "finish_time", "elapsed_seconds", "contributor_uuid"]
               ].set_index("quiz_task_uuid")
    quest_label_text = data_hunt.loc[:, ["question_label", "question_text"]].drop_duplicates().set_index("question_label")
    answer_id_text = data_hunt.loc[:, ["answer_label", "answer_content", "answer_uuid", "answer_text"]].drop_duplicates()
    starts_ends = data_hunt.loc[:,["quiz_task_uuid", "question_label", "start_pos", "end_pos"]].set_index("quiz_task_uuid")
    highlight = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "contributor_uuid",
                                  "target_text", "highlight_count", "answer_uuid", "answer_content"]
                ].set_index("quiz_task_uuid")


    # Creates a dictionary categorized by task_uuid
    for i in range(len(task_id_url_data)):
        record = task_id_url_data.iloc[i, :]
        uuid = record.loc["quiz_task_uuid"]
        url = record.loc["task_url"]
        tua_uuid = record.loc["tua_uuid"]
        article_record = task_article.loc[uuid, :]

        # uberDict is indexed by uuid, which has two keys: taskData and quesData
        task = uberDict[uuid] = {}
        task['taskData'] = {
            "task_uuid": uuid,
            "task_url": url,
            "tua_uuid": tua_uuid,
            "article_name": article_record.loc["article_batch_name"],
            "article_number": article_record.loc["article_number"],
            "article_filename": article_record.loc["article_filename"],
            "article_sha256": article_record.loc["article_sha256"],
            "article_text_length": article_record.loc["article_text_length"],
            "article_num": 0, #TODO
        }

        # computes the start and end lists
        starts, ends = getStartsEndsLists(starts_ends, uuid)

        # gets highlighted information
        highlightGrouped = highlight.loc[uuid].groupby("question_label")
        hlUsers = highlightGrouped["contributor_uuid"].apply(list)
        target_text = highlightGrouped["target_text"].apply(list) # Don't know for sure
        answer_content = highlight.loc[uuid].groupby("question_label")["answer_content"].apply(list)

        # for each task, creates a new questionData that parses through related question and answer
        ques = uberDict[uuid]['quesData'] = {}
        for question_label in list(starts.index):
            ques[question_label] = {
                    "starts" : starts.loc[question_label],
                    "ends" : ends.loc[question_label],
                    "hlUsers" : hlUsers[question_label],
                    "target_text" : target_text[question_label],
                    "answer_content": answer_content[question_label],
                    "question_text": quest_label_text.loc[question_label, "question_text"]
                }
    return uberDict



def getStartsEndsLists(starts_ends, uuid):
    """
    Gets the starts and ends DataFrame by uuid.
    Outputs a pair of DataFrames. Each entry is a LIST of start or end positions
    """
    grouped = starts_ends.loc[uuid].groupby("question_label")
    return grouped['start_pos'].apply(list), grouped['end_pos'].apply(list)


def printColumnUniqueVals(data):
    for col in data.columns:
        print("{:30} {:>8}".format("Column: " + col, len(data[col].unique())))



