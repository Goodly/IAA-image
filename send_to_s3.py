import os

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
    for root, dir, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
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