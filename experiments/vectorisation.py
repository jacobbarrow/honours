import numpy

from gensim.models import Word2Vec

import utils
from db_files import load


def getAverageVector(words):
    total = 0
    for word in words.split(' '):
        try:
            total += model.wv[word.lower()]
        except KeyError:
            pass

    return total


articles = load.FNC()
model = Word2Vec.load('vectorisation_model/vector.model')

agree_differences = []
disagree_differences = []

for i, article in enumerate(articles.values()):
    try:
        headline_vec = getAverageVector(article['headline'])
        body_vec = getAverageVector(article['body'])

        difference = model.wv.cosine_similarities(headline_vec, [body_vec])[0]

        if(article['stance'] == 'agree'):
            agree_differences.append(difference)

        else:
            disagree_differences.append(difference)

    except numpy.AxisError:
        pass

significance = utils.calcSignificance(agree_differences, disagree_differences)

p_value = significance['p']
distribution = significance['distribution']

print(f'Agree avg     {numpy.mean(agree_differences)}')
print(f'Disagree avg  {numpy.mean(disagree_differences)}')
print(f'Significance  {round(p_value, 5)} ({distribution})')
