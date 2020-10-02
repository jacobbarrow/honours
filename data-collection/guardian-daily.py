import requests
import time
from datetime import datetime
import re
import sqlite3
import logging
import sys
import hashlib

from bs4 import BeautifulSoup

logger = logging.getLogger('guardian-daily')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('daily.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# Set up database
db = sqlite3.connect('guardian-daily.sqlite')
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


# Used to convert month string to int
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

feeds = ['uk/rss', 'world/rss']

for feed in feeds:
    logger.debug('[GUARDIAN@{0}] Scraping {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), feed))


    feed_request = requests.get('https://www.theguardian.com/{0}'.format(feed))
    feed_soup = BeautifulSoup(feed_request.content, features='lxml')

    for article_listing in feed_soup.find_all('item'):
        # Need to be very excepting of whatever this throws up - runs as a cron job so can't have it crashing
            article_url = article_listing.find('guid').get_text()
            split_url = article_url.split('/')

            bad_paths = ['/audio/', '/live/', '/gallery/', '/blog/', '/video/']
            if not any(path in article_url for path in bad_paths):
                try:

                    article_id = hashlib.md5(article_url.encode('utf-8')).hexdigest()

                    db_cursor.execute("SELECT Count() FROM articles WHERE id='{0}'".format(article_id))
                    already_scraped = db_cursor.fetchone()[0]

                    if not already_scraped:
                        article_request = requests.get(article_url)

                        article_soup = BeautifulSoup(article_request.content, features='html5lib')

                        article_headline = article_soup.find('h1').get_text().strip()


                        # Find where the year is in URL
                        for index, section in enumerate(split_url):
                            if section.startswith('20') and len(section) is 4:
                                year_index = index

                        year = split_url[year_index]
                        month =  months.index(split_url[year_index+1]) + 1
                        day = int(split_url[year_index+2])

                        

                        article_date = '{0}-{1:02d}-{2:02d}'.format(year, month, day) 

                        # Article body
                        article_inner = article_soup.find('div', class_='content__article-body')

                        try:
                            # Guardian just uses straight p tags for content, which is very handy
                            article_body = ""
                            for p in article_inner.find_all('p'):
                                article_body += '{0}\n'.format(p.get_text())

                            try:
                                db_cursor.execute('INSERT INTO articles (id, headline, body, date) VALUES (?,?,?,?)', (article_id, article_headline, article_body, article_date))
                                db.commit()
                                print("added {0}".format(article_headline))
                            except sqlite3.IntegrityError:
                                print('already added {0}'.format(article_headline))

                        except AttributeError:
                            print('Rate limited! ({0})'.format(article_url))


                except Exception:
                    print('{0}: {1}'.format(article_url, sys.exc_info()))
                    logger.warning('[GUARDIAN@{0}] {1}: {2}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_url, sys.exc_info()))
                    

db.close()

print('All done!')