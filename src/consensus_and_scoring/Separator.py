import pandas as pd
import numpy as np
import os
import csv
from dataV3 import make_directory

from dataV3 import get_indices_hard


def splitcsv(directory, pointsFile = None, viz_dir = None, textseparator = '//', reporting = True):
    #print('splitting')
    if pointsFile is None:
        pointsFile = findWeights(directory)
        #print(pointsFile)
        print(directory, pointsFile)
        pointsdf = pd.read_csv(directory+'/'+pointsFile)
    else:
        pointsdf = pointsFile
    #print(pointsdf)
    valid_points = pointsdf[~pd.isna(pointsdf['article_sha256'])]
    valid_points = valid_points[valid_points['points']!=0]
    articles = np.unique(valid_points['article_sha256'])
    final_cols = ['Article ID', 'Credibility Indicator ID', 'Credibilty Indicator Category',
                  'Credibility Indicator Name', 'Points', 'Indices of Label in Article', 'Start', 'End', 'target_text']


    for art in articles:
        final_out = [final_cols]
        artdf = valid_points[valid_points['article_sha256'] == art]
        if len(artdf)<1:
            artdf = pointsdf[pointsdf['article_sha256'] == art]
        if reporting:
            art_id = artdf['article_id'].iloc[0]
        else:
            art_id = art
        schema = np.unique(artdf['Schema'])
        for s in schema:
            sch_df = artdf[artdf['Schema'] == s]
            cred_cat = sch_df['Schema'].iloc[0]
            count = 0
            cred_id = cred_cat[0]+str(count)
            #Following loop goes through each entry in the weights table
            for j in range(sch_df.shape[0]):
                start = -1
                end = -1
                cred_ind_name = sch_df['Label'].iloc[j]
                indices = sch_df['highlighted_indices'].iloc[j]
                points = sch_df['points'].iloc[j]
                text = sch_df['target_text'].iloc[j]
                #if there is a unitization
                if not (isinstance(indices, float)) and (not (isinstance(indices, str)) or len(indices) > 2):
                    indices = get_indices_hard(indices)
                    sei = indicesToStartEnd(indices)
                    starts = sei[0]
                    ends = sei[1]
                    chunks = sei[2] #chunk of the index that we're investigating
                    for k in range(len(starts)):
                        start = starts[k]
                        end = ends[k]
                        indices = chunks[k]
                        #addend = pd.DataFrame([art_id, cred_id, cred_cat, cred_ind_name, points, indices,start,
                        #                       end])
                        addend = [art_id, cred_id, cred_cat, cred_ind_name, points, indices,start, end, text]
                        final_out.append(addend)
                        #set point value to 0 to avoid double counting
                        #the visualizatio sums up the column and automatically combines separate unitizations with
                        #the same label
                        points = 0
                else:
                    #addend = pd.DataFrame([art_id, cred_id, cred_cat, cred_ind_name, points, indices, start, end])
                    addend = [art_id, cred_id, cred_cat, cred_ind_name, points, indices, start, end, text]
                    final_out.append(addend)
                #final_out = pd.concat([final_out, addend], axis =0, names = final_cols)
        final_out.append([None, None, None, None,None,None,None, None, None])
        path = directory + '/VisualizationData_' + art_id + '.csv'
        print("EXPORTENg  "+path)
        viz_dir = make_directory(viz_dir)
        scores = open(viz_dir + '/VisualizationData_' + art_id + '.csv', 'w', encoding='utf-8')
        with scores:
            writer = csv.writer(scores)
            writer.writerows(final_out)
        #final_out.to_csv(directory + '/VisualizationData_' + str(art) + '.csv', index=False, encoding='utf-8')
        #print('exporting Finale')



def findWeights(directory):
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'AssessedPoints' in file:
                return file


def indicesToStartEnd(indices):
    starts = []
    ends = []
    breakpointer = []
    last = -1
    arr = np.array(indices)
    if len(indices)<1:
        return [-1],[-1], [-1]
    for i in range(len(indices)):
        if indices[i]-last>1 and indices[i] not in starts:
            starts.append(indices[i])
            ends.append(indices[i-1])
            breakpointer.append(i)
        last = indices[i]
    chunks = []
    breakpointer.append(len(indices)-1)
    base = 0
    for i in range(1, len(breakpointer)):
        chunks.append(indices[base:breakpointer[i]])
        base = breakpointer[i]
    #ends.append(indices[len(indices)-1])
    return sorted(starts), sorted(ends), sorted(chunks)
#splitcsv('scoring_covid')