import pandas as pd
import numpy as np
import os
import json
import csv

def splitcsv(directory):
    #print('splitting')
    pointsFile = findWeights(directory)
    #print(pointsFile)
    pointsdf = pd.read_csv(directory+'/'+pointsFile)
    #print(pointsdf)
    valid_points = pointsdf[~pd.isna(pointsdf['article_sha256'])]
    articles = np.unique(valid_points['article_sha256'])
    final_cols = ['Article ID', 'Credibility Indicator ID', 'Credibilty Indicator Category',
                  'Credibility Indicator Name', 'Points', 'Indices of Label in Article', 'Start', 'End']


    for art in articles:
        final_out = [final_cols]
        artdf = valid_points[valid_points['article_sha256'] == art]
        art_id = artdf['article_sha256'].iloc[0]
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
                #if there is a unitization
                if not (isinstance(indices, float)) and (not (isinstance(indices, str)) or len(indices) > 1):
                    indices = json.loads(indices)
                    starts, ends = indicesToStartEnd(indices)

                    for k in range(len(starts)):
                        start = starts[k]
                        end = ends[k]
                        #addend = pd.DataFrame([art_id, cred_id, cred_cat, cred_ind_name, points, indices,start,
                        #                       end])
                        addend = [art_id, cred_id, cred_cat, cred_ind_name, points, indices,start, end]
                        final_out.append(addend)
                        #set point value to 0 to avoid double counting
                        #the visualizatio sums up the column and automatically combines separate unitizations with
                        #the same label
                        points = 0
                else:
                    addend = pd.DataFrame([art_id, cred_id, cred_cat, cred_ind_name, points, indices, start, end])
                    addend = [art_id, cred_id, cred_cat, cred_ind_name, points, indices, start, end]
                    final_out.append(addend)
                #final_out = pd.concat([final_out, addend], axis =0, names = final_cols)

        path = directory + '/VisualizationData_' + str(art) + '.csv'
        print("EXPORTENg  "+path)
        scores = open(directory + '/VisualizationData_' + str(art) + '.csv', 'w', encoding='utf-8')
        with scores:
            writer = csv.writer(scores)
            writer.writerows(final_out)
        #final_out.to_csv(directory + '/VisualizationData_' + str(art) + '.csv', index=False, encoding='utf-8')
        #print('exporting Finale')



def findWeights(directory):
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'SortedPts' in file:
                return file


def indicesToStartEnd(indices):
    starts = []
    ends = []
    last = -1
    arr = np.array(indices)
    if len(indices)<1:
        return [-1],[-1]
    for i in range(len(indices)):
        if indices[i]-last>1 and indices[i] not in starts:
            starts.append(indices[i])
            ends.append(indices[i-1])
        last = indices[i]
    #ends.append(indices[len(indices)-1])
    return sorted(starts), sorted(ends)
#splitcsv('scoring_urap')