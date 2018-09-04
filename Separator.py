import pandas as pd
import numpy as np
import os

def splitcsv(directory):
    print('splitting')
    pointsFile = findMaster(directory)
    pointsdf = pd.read_csv(directory+'/'+pointsFile)
    print(pointsdf)
    articles = np.unique(pointsdf['Article ID'])
    for art in articles:
        artdf = pointsdf[pointsdf['Article ID'] == art]
        print('exporting Finale')
        artdf.to_csv(directory+'/VisualizationData_'+art[:8]+'.csv', encoding='utf-8')

def findMaster(directory):
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'SortedPts_' in file:
                return file