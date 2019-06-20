import pandas as pd
import numpy as np
import os

def splitcsv(directory):
    #print('splitting')
    pointsFile = findWeights(directory)
    #print(pointsFile)
    pointsdf = pd.read_csv(directory+'/'+pointsFile)
    #print(pointsdf)
    valid_points = pointsdf[~pd.isna(pointsdf['article_sha256'])]
    articles = np.unique(valid_points['article_sha256'])
    valid_points['starts'] = np.zeros(valid_points.shape[0])
    for i in range(articles.shape[0]):
        indices = valid_points['highlighted_indices'].iloc[i]
        starts, ends = indicesToStartEnd(indices)
        valid_points.iloc[i, valid_points.columns.get_loc('starts')] = starts
        valid_points.iloc[i, valid_points.columns.get_loc('starts')] = ends
    for art in articles:
        artdf = valid_points[valid_points['article_sha256'] == art]
        print(len(artdf))
        artdf = artdf.drop_duplicates(subset = ['Points', 'Credibility Indicator Name', 'Start', 'End'])
        print(len(artdf))
        print('exporting Finale')
        artdf.to_csv(directory+'/VisualizationData_'+str(art)+'.csv', index = False, encoding='utf-8')


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
splitcsv('scoring_urap')