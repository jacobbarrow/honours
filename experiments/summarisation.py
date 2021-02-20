import numpy

import matplotlib.pyplot as plt

import utils
from fnc import load

import spacy

from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation

extra_words=list(STOP_WORDS)+list(punctuation)+['\n']
nlp=spacy.load('en')

#articles = load.FNC()

doc = """
More heavy snow is forecast for the east and south-east of England, with severe weather warnings in force.

The Met Office said it was "bitterly cold" due to Storm Darcy's strong easterly winds, with temperatures in parts of the UK around freezing.

An amber warning - meaning travel disruption and power cuts are likely - is in place until midday on Monday.

There is also an amber warning for snow in the East Midlands and Yorkshire and Humber until 14:00 GMT.

And less severe yellow warnings for snow and ice have been issued for large parts of England, Scotland and Northern Ireland.

The conditions have led to some vaccination centres being closed, including several in Essex and Suffolk, as well as in Surrey.

Further snowfall in some eastern parts of the country could bring up to 15cm of snow on Monday, with a few lighter flurries elsewhere in the UK, BBC Weather forecasters said.

There could also be as much as 15cm in parts of the East Midlands and Yorkshire and Humber, particularly over the Lincolnshire Wolds.

It comes after widespread snowfall in eastern regions of the UK and 14cm (5.5in) of snow was recorded at Manston, Kent, on Sunday evening.

In Suffolk, a man who is thought to have been kitesurfing died on Sunday after being found on a beach in stormy conditions.

Emergency services were called after reports of a person in the North Sea off Walberswick and the man was later found on the shore by members of the public. He died at the scene. 
"""

docx = nlp(doc)


all_words=[word.text for word in docx]

Freq_word={}
for w in all_words:
      w1=w.lower()
      if w1 not in extra_words and w1.isalpha():
            if w1 in Freq_word.keys():
                Freq_word[w1]+=1
            else:
                Freq_word[w1]=1

val=sorted(Freq_word.values())
max_freq=val[-3:]
print("Topic of document given :-")
for word,freq in Freq_word.items():
    if freq in max_freq:
        print(word ,end=" ")
    else:
        continue