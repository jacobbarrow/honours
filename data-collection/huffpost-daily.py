import requests
import time
from datetime import datetime
import re
import sqlite3
import logging
import sys
import hashlib

from bs4 import BeautifulSoup

logger = logging.getLogger('huffpost-daily')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('daily.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# Set up database
db = sqlite3.connect('huffpost-daily.sqlite')
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

user_agent_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

feeds = ['feeds/index.xml']

for feed in feeds:
    print('Scraping feed {0}'.format(feed))
    logger.debug('[HUFFPOST@{0}] Scraping {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), feed))

    feed_request = requests.get('https://www.huffingtonpost.co.uk/{0}'.format(feed), headers=user_agent_header)
    feed_soup = BeautifulSoup(feed_request.content, features='xml')

    # HuffPost puts all the content in the RSS feed, so no need to make extra requests
    for article_listing in feed_soup.find_all('item'):
        article_url = article_listing.find('link').get_text()

        article_id = hashlib.md5(article_url.encode('utf-8')).hexdigest()
        db_cursor.execute("SELECT Count() FROM articles WHERE id='{0}'".format(article_id))
        already_scraped = db_cursor.fetchone()[0]

        if not already_scraped:
           
            raw_date = article_listing.find('pubDate').get_text()
            # This ugly line converts the date to a datetime object, then formats it using YYYY-MM-DD
            article_date = datetime.strptime(raw_date, '%a, %d %b %Y %H:%M:%S +0000').strftime('%Y-%m-%d')
            
            article_headline = article_listing.find('title').get_text().strip()

            article_body_html = article_listing.find('description').get_text()
            article_body_soup = BeautifulSoup(article_body_html, features='lxml')

            for tweet in article_body_soup.find_all('div', class_='twitter-tweet'):
                tweet.extract()

            article_body = ""
            for p in article_body_soup.find_all('p'):
                if 'https://' not in p.get_text() and 'twitter.com/' not in p.get_text():
                    article_body += '{0}\n'.format(p.get_text().strip())


            try:
                db_cursor.execute('INSERT INTO articles (id, headline, body, date) VALUES (?,?,?,?)', (article_id, article_headline, article_body, article_date))
                db.commit()
                print("added {0}".format(article_headline[:30]))
            except sqlite3.IntegrityError:
                print('already added {0}'.format(article_headline))

db.close()

print('All done!')