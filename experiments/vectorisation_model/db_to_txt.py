import sqlite3
import csv
import sys

SOURCES = ['bbc-daily', 'guardian-daily', 'mail-daily', 'huffpost-daily']

headlines_file = open('headlines.txt', 'w')
bodies_file = open('bodies.txt', 'w')

for source in SOURCES:
    print(f'starting on {source}')

    db = sqlite3.connect('../../data-collection/{0}.sqlite'.format(source))
    cursor = db.cursor()

    for row in cursor.execute('SELECT headline, body FROM articles'):
        headlines_file.write(f'{row[0]}\n')
        bodies_file.write(f'{row[1]}\n')


csv.field_size_limit(sys.maxsize)

with open('articles.csv', newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    articles_count = 0
    for row in csv_reader:
        headlines_file.write(f'{row[1]}\n')
        bodies_file.write(f'{row[2]}\n')
        articles_count += 1
        if articles_count > 50000:
            break

headlines_file.close()
bodies_file.close()
