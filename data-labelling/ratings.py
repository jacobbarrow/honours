import sqlite3

create_table_sql = """
CREATE TABLE ratings(
    id INTEGER PRIMARY KEY,
    article_id TEXT,
    rating INTEGER,
    time_taken INTEGER,
    FOREIGN KEY(article_id) REFERENCES article(id)
);
"""

least_rated_article_sql = """
SELECT articles.id, articles.headline, articles.body, Count(ratings.id) AS t
FROM articles
LEFT JOIN ratings on articles.id = ratings.article_id
GROUP BY articles.id
ORDER BY t ASC
LIMIT 1
"""

with sqlite3.connect('data/ratings.sqlite') as db:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT Count() FROM ratings")
        print('Already have {0} ratings'.format(cursor.fetchone()[0]))
    except sqlite3.OperationalError:
        cursor.execute(create_table_sql)

def add(article_id, rating, time_taken):
    with sqlite3.connect('data/ratings.sqlite') as db:
        cursor = db.cursor()
        cursor.execute('INSERT INTO ratings (article_id, rating, time_taken) VALUES (?,?,?)', (article_id, rating, time_taken))
        db.commit()

def getLeastRatedArticle():
    with sqlite3.connect('data/ratings.sqlite') as db:
        cursor = db.cursor()
        cursor.execute(least_rated_article_sql)
        raw_article = cursor.fetchone()
        article = {
            'id': raw_article[0],
            'headline': raw_article[1],
            'body': raw_article[2]
        }

    return article
