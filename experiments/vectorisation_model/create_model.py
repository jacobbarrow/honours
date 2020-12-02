from nltk.tokenize import sent_tokenize, word_tokenize

from gensim.models import Word2Vec

import os
import csv
import sys
import time
csv.field_size_limit(sys.maxsize)


class SentencesReader():
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for csv_file in os.listdir(self.dirname):
            print(f'Loading {csv_file}...')
            start_time = time.time()
            with open(self.dirname+'/'+csv_file, newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csv_reader:
                    for sent in sent_tokenize(row[2]):
                        words = []

                        for word in word_tokenize(sent):
                            words.append(word.lower())

                        yield words
            print(f'Took {round(time.time() - start_time, 2)}s')


print('Setting up reader...')
reader = SentencesReader('~/Documents/Uni/honours/experiments/db_files')

print('Creating model...')
model = Word2Vec(reader, min_count=2, workers=8, iter=10)
model.save("vector.model")

print('Done!')
