import numpy

import utils
from db_files import load

articles = load.FNC()

max_frequency_cache = {}


def frequency(word, document):
    return document.split().count(word)


def termFrequency(word, document, domain):
    global max_frequency_cache

    word_frequency = frequency(word, document)

    # Stops having to iterate through whole domain each time
    if word in max_frequency_cache:
        return word_frequency / max_frequency_cache[word]

    max_frequency = max([frequency(word, this_doc) for this_doc in domain])

    if max_frequency == 0:
        max_frequency = 0.00001  # Solves division by 0

    max_frequency_cache[word] = max_frequency

    return word_frequency / max_frequency


def inverseDocumentFrequency(word, domain):

    number_of_documents_word_appears_in = 0
    for document in domain:
        if word in document:
            number_of_documents_word_appears_in += 1

    return len(domain) / number_of_documents_word_appears_in


def tfidf(word, document, domain):
    return termFrequency(word, document, domain) * \
        inverseDocumentFrequency(word, domain)


# Construct the domain (array of article headlines + bodies)
domain = []
for article in articles.values():
    domain.append(article['headline'] + ' ' + article['body'])

agree_means = []
disagree_means = []
for article in articles.values():
    tfidfs = []
    for word in article['headline']:
        tfidfs.append(tfidf(word, article['body'], domain))

    mean = numpy.mean(tfidfs)

    if article['stance'] == 'agree':
        agree_means.append(mean)
    else:
        disagree_means.append(mean)


significance = utils.calcSignificance(agree_means, disagree_means)

p_value = significance['p']
distribution = significance['distribution']

print(f'Agree avg     {numpy.mean(agree_means)}')
print(f'Disagree avg  {numpy.mean(disagree_means)}')
print(f'Significance  {round(p_value, 5)} ({distribution})')
