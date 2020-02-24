import csv
import sys
import shutil
import fileinput
import os
import os.path


def visualize(articleID, prefix = ''):
    print("visualizing", articleID, prefix)

    shutil.copy("Visualization.html", os.getcwd() + "/TestBed")
    curName = "TestBed/Visualization" +prefix+ articleID + ".html"
    os.rename("TestBed/Visualization.html", curName)
    print('curName',curName)
    shutil.move(curName, os.getcwd())
    curName = "Visualization" + prefix+articleID + ".html"

    text = ""

    #with open(articleID + "SSSArticle.txt", encoding='utf-8') as file:
    #    text = file.read()

    with fileinput.FileInput(curName, inplace=True) as file:
        for line in file:
            print(line.replace("ARTICLEIDHERE", articleID, 1), end='')

    #with fileinput.FileInput(curName, inplace=True) as file:
    #    for line in file:
    #        print(line.replace("ARTICLETEXTHERE", text, 1), end='')

    cmdString = "aws s3 mv "+ curName + " s3://publiceditor.io/Articles/" + curName + " --acl public-read-write"
    os.system(cmdString)
    print('viz sent to aws')

visualize