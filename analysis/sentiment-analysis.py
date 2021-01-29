import os
import csv
import sys
from datetime import datetime 

import matplotlib.pyplot as plt 
from matplotlib.dates import drange 

import numpy as np 

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

csv.field_size_limit(sys.maxsize)
dir_path = os.path.dirname(os.path.realpath(__file__))

analyser = SentimentIntensityAnalyzer()

def analyse(filename, limit=None):
    sentiments = []

    with open(f'db_files/{filename}.csv', newline='\n') as csvfile:
        
        csv_reader = csv.DictReader(csvfile, delimiter=",", quotechar="|")

        print('read')
        for i, row in enumerate(csv_reader):
            # date = datetime.strptime(row['date'], '%Y-%m-%d')
            if i % 50 == 0:
                print(i)
                sentiments.append(analyser.polarity_scores(row['body'])['pos'])
            if limit is not None and i > limit:
                break

    return sentiments

plt.plot(analyse('independent-archive', limit=None))

plt.show()
