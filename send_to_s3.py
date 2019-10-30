import os
import pandas as pd
import numpy as np
from time import sleep
def send_s3(scoring_dir, input_dir):
    print("pushing to s3")
    art_ids = []
    for root, dir, files in os.walk(scoring_dir):
        for file in files:
            if file.endswith('.csv') and 'VisualizationData_' in file:
                cmd_str = "aws s3 cp "+ scoring_dir+'/'+file+" s3://publiceditor.io/Articles/"+file+" --acl public-read"
                os.system(cmd_str)
                print('calling:',cmd_str)
                id = file.split('Data_', 1)[1][:-4]
                #-4 to make sure the .csv goes away
                art_ids.append(id)
    print(art_ids)
    #Also blap the texts to S3 for visualizations
    #first rename
    filenames = []
    sha_256s = []
    #have to look at all of them in case one article didn't get sent to a certain specialist
    for root, dir, files in os.walk(input_dir):
        for file in files:
            if 'Answers' in file and 'lock' not in file:
                print(file)
                ans = pd.read_csv(os.path.join(input_dir, file))
                filnams = ans['article_filename']
                here_textfiles = np.unique(filnams)
                for t in here_textfiles:
                    if not t in filenames:
                        filenames.append(t)
                        sha_256 = ans[ans['article_filename'] == t]['article_sha256'].iloc[0]
                        sha_256s.append(sha_256)
    for i in range(len(filenames)):
        print(filenames[i])
        print(sha_256s[i])

    in_path = os.path.realpath(input_dir)
    text_dir = in_path+'/texts'
    for filename in os.listdir(text_dir):
        i = filenames.index(filename)
        new_sha = sha_256s[i]
        new_name = new_sha+'SSSArticle.txt'
        src = os.path.join(text_dir, filename)
        dst = os.path.join(text_dir, new_name)
        os.rename(src, dst)
    print("done renaming")
    sleep(5)
    for filename in os.listdir(text_dir):
        print(filename)


    #now send
    for root, dir, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                print("pushing text", file)
                if 'SSSArticle' in file:
                    dir_path = os.path.dirname(os.path.realpath(file))
                    print('dir', dir_path)
                    input_path = os.path.join(dir_path, input_dir)
                    file_path = os.path.join(input_path, 'texts/')
                    text_path = os.path.join(file_path, file)
                    cmd_str = "aws s3 cp " + text_path + " s3://publiceditor.io/Articles/" + \
                              file + " --acl public-read"
                    os.system(cmd_str)
                else:
                    print("!!!YOU IDIOT!!!!--make sure the text file's format is SHA256 + SSSArticle.txt, where SHA256 "+
                          "is the \n"+
                          "article's sha256 and SSSArticle.txt is that, regardless of article title")
    return art_ids

#send_s3('scoring_sep_urap', 'sep_urap')