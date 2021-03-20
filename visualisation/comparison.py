import json

import matplotlib.pyplot as plt
from matplotlib.dates import (YEARLY, DateFormatter, rrulewrapper, RRuleLocator, drange)
import datetime

import numpy as np

ROLLING_AVG = 14
SENTIMENT_TYPE = 'body'

sources = {'BBC': 'bbc', 'Daily Mail': 'dai', 'Guardian': 'gua', 'HuffPost': 'huff'}
raw_source_data = {}
source_data = {}
for source_name, source_code in sources.items():
    source_file_name = f'analysis-{source_code}d.json'
    with open(source_file_name) as source_file: 
        raw_source_data[source_name] = json.load(source_file)[SENTIMENT_TYPE]
        source_data[source_name] = []
        


start = datetime.date(2020, 10, 9)
end = datetime.date(2021, 1, 1)

days = []

current_day = start
while current_day < end:
    days.append(current_day)
    for source_name, raw_data in raw_source_data.items():
        source_data[source_name].append(raw_data[str(current_day)])

    
    current_day += datetime.timedelta(days=1)

for source_name, data in source_data.items():
    # Rolling avg from https://stackoverflow.com/a/44797397/2650094
    plt.plot(days[ROLLING_AVG-1:], np.convolve(data, np.ones(ROLLING_AVG)/ROLLING_AVG, mode='valid'), label=source_name)


plt.xlabel('Date')
plt.ylabel(f'{SENTIMENT_TYPE.capitalize()} Sentiment')

plt.legend(loc=2)

fig, ax = plt.subplots()
ax.set_xticks(5)

plt.gcf().autofmt_xdate()
plt.show()

