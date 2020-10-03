import requests
import time
from datetime import datetime
import re
import sqlite3
import logging
import sys
import hashlib

from bs4 import BeautifulSoup

logger = logging.getLogger('mail-daily')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('daily.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# Set up database
db = sqlite3.connect('mail-daily.sqlite')
db_cursor = db.cursor()

create_table_sql = """
CREATE TABLE articles(
   id TEXT PRIMARY KEY,
   headline TEXT,
   body TEXT,
   date TEXT
);
"""
try:
    db_cursor.execute("SELECT Count() FROM articles")
    print('Already have {0} articles in db'.format(db_cursor.fetchone()[0]))
except sqlite3.OperationalError:
    db_cursor.execute(create_table_sql)


feeds = ['news/index.rss', 'news/articles.rss']

for feed in feeds:
    print('Scraping feed {0}'.format(feed))
    logger.debug('[MAIL@{0}] Scraping {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), feed))

    feed_request = requests.get('https://www.dailymail.co.uk/{0}'.format(feed))
    feed_soup = BeautifulSoup(feed_request.content, features='lxml')

    for article_listing in feed_soup.find_all('item'):
        article_url = article_listing.find('guid').get_text()


        try:
            raw_date = article_listing.find('pubdate').get_text()
            # This ugly line converts the date to a datetime object, then formats it using YYYY-MM-DD
            article_date = datetime.strptime(raw_date, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')


            article_id = hashlib.md5(article_url.encode('utf-8')).hexdigest()

            db_cursor.execute("SELECT Count() FROM articles WHERE id='{0}'".format(article_id))
            already_scraped = db_cursor.fetchone()[0]

            if not already_scraped:
                article_request = requests.get(article_url)

                article_soup = BeautifulSoup(article_request.content, features='lxml')
                article_headline = article_soup.find('h2').get_text().strip()

                # Article body
                article_inner = article_soup.find('div', {'itemprop': 'articleBody'})

                article_body = ""
                for p in article_inner.find_all('p'):
                    article_body += '{0}\n'.format(p.get_text())

                try:
                    db_cursor.execute('INSERT INTO articles (id, headline, body, date) VALUES (?,?,?,?)', (article_id, article_headline, article_body, article_date))
                    db.commit()
                    print("added {0}".format(article_headline[:30]))
                except sqlite3.IntegrityError:
                    print('already added {0}'.format(article_headline))


        except Exception:
            print('{0}: {1}'.format(article_url, sys.exc_info()))
            logger.warning('[MAIL@{0}] {1}: {2}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_url, sys.exc_info()))
                

db.close()

print('All done!')