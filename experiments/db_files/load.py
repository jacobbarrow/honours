import os
import csv
import sys

csv.field_size_limit(sys.maxsize)
dir_path = os.path.dirname(os.path.realpath(__file__))


def FNC():
    articles = {}

    with open(f'{dir_path}/fnc/train_stances.csv', newline='\n') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # Disregard unrelated stances - out of scope
            if not row['Stance'] in ['unrelated', 'discuss']:
                articles[row['Body ID']] = {'headline': row['Headline'],
                                            'stance': row['Stance']}

    with open(f'{dir_path}/fnc/train_bodies.csv', newline='\n') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            try:
                articles[row['Body ID']]['body'] = row['articleBody']
            except KeyError:
                pass  # Relates to an article we've discarded

    return articles


if __name__ == '__main__':
    print(f'FNC length: {len(FNC())}')
