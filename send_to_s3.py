import os

def send_s3(scoring_dir):
    print("pushing to s3")
    for root, dir, files in os.walk(scoring_dir):
        for file in files:
            if file.endswith('.csv') and 'VisualizationData_' in file:
                cmd_str = "aws s3 mv "+ scoring_dir+'/'+file+" s3://publiceditor.io/Articles/"+file
                os.system(cmd_str)
                print('calling:',cmd_str)