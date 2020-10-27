import sqlite3
import random

SUBSET_SIZE = 300
SOURCES = ['bbc-daily', 'guardian-daily', 'mail-daily', 'huffpost-daily', 'independent-archive']

source_dbs = []
for source in SOURCES:
    db = sqlite3.connect('../../data-collection/{0}.sqlite'.format(source))
    connection = {
        'name': source,
        'db': db,
        'cursor': db.cursor()
    }
    source_dbs.append(connection)

subset_db = sqlite3.connect('ratings.sqlite')
subset_db_cursor = subset_db.cursor()

create_table_sql = """
CREATE TABLE articles(
   id TEXT PRIMARY KEY,
   headline TEXT,
   body TEXT,
   date TEXT,
   source TEXT
);
"""
articles_collected = 0

try:
    subset_db_cursor.execute("SELECT Count() FROM articles")
    articles_collected = int(subset_db_cursor.fetchone()[0])
    print('Already have {0} articles in subset'.format(articles_collected))
except sqlite3.OperationalError:
    subset_db_cursor.execute(create_table_sql)

articles_to_collect = SUBSET_SIZE - articles_collected

print('Will randomly pick {0} articles from the databases'.format(articles_to_collect))

for _ in range(articles_to_collect):

    # Might pick out an article we've already got, so by sure not to
    article_collected = False
    while not article_collected:
        source_db = random.choice(source_dbs)
        source_db['cursor'].execute('SELECT * FROM articles WHERE id IN (SELECT id FROM articles ORDER BY RANDOM() LIMIT 1)')
        article = source_db['cursor'].fetchone()
        try:
            subset_db_cursor.execute('INSERT INTO articles (id, headline, body, date, source) VALUES (?,?,?,?,?)', (article[0], article[1], article[2], article[3], source_db['name']))
            subset_db.commit()
            article_collected = True
        except sqlite3.IntegrityError:
            continue

subset_db.close()
print('done')




