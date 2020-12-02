import numpy

import matplotlib.pyplot as plt

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import utils
from db_files import load

analyzer = SentimentIntensityAnalyzer()
articles = load.FNC()

STANCES = ['agree', 'disagree']
KEYS = ['pos', 'neg', 'neu', 'compound']
LABELS = ['Positive', 'Negative', 'Neutral', 'Compound']

# Set up an empty 2d dictionary
differences = {}
for stance in STANCES:
    differences[stance] = {}
    for key in KEYS:
        differences[stance][key] = []


def _autolabel(ax, bars):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for bar in bars:
        height = bar.get_height()
        ax.annotate('{}'.format(round(height, 2)),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def generateVis(limit=None):
    for i, article in enumerate(articles.values()):
        headline_sentiment = analyzer.polarity_scores(article['headline'])
        body_sentiment = analyzer.polarity_scores(article['body'])

        for key in KEYS:
            # Sentiment values range from -1 to 1, so take half the difference
            percentage = abs(headline_sentiment[key] - body_sentiment[key])/2
            differences[article['stance']][key].append(percentage)

        if limit and i > limit:
            break

    _, ax = plt.subplots()

    label_locations = numpy.arange(len(LABELS))
    bar_width = 0.4

    means = {}
    for index, stance in enumerate(STANCES):
        means[stance] = []
        for key in KEYS:
            means[stance].append(numpy.mean(differences[stance][key]))

        bar_location = label_locations + 0.2 - (bar_width * index)
        bars = ax.bar(bar_location, means[stance], bar_width, label=stance)
        _autolabel(ax, bars)

    for key in KEYS:
        significance = utils.calcSignificance(differences['agree'][key],
                                              differences['disagree'][key])
        p_value = significance['p']
        distribution = significance['distribution']

        print(f'{key}: {round(p_value, 5)} ({distribution})')

    ax.set_title('Distribution of types of sentiment by percentage difference')
    ax.set_ylabel('Mean difference')
    ax.set_xlabel('Sentiment')
    ax.set_xticks(label_locations)
    ax.set_xticklabels(LABELS)
    ax.legend()
    plt.show()


if __name__ == '__main__':
    generateVis()
