import requests
import time
from datetime import datetime
import re
import sqlite3
import logging
import sys
from bs4 import BeautifulSoup

logger = logging.getLogger('bbc-daily')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('daily.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# Set up database
db = sqlite3.connect('bbc-daily.sqlite')
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

feeds = ['news/rss.xml', 'news/world/rss.xml', 'news/uk/rss.xml']

for feed in feeds:
    print('scraping {0}'.format(feed))

    feed_request = requests.get('http://feeds.bbci.co.uk/{0}'.format(feed))
    feed_soup = BeautifulSoup(feed_request.content, features='lxml')

    for article_listing in feed_soup.find_all('item'):
        # Need to be very excepting of whatever this throws up - runs as a cron job so can't have it crashing
        try:
            article_url = article_listing.find('guid', {'ispermalink': 'true'}).get_text()

            article_id = article_url.split('/')[-1]

            db_cursor.execute("SELECT Count() FROM articles WHERE id='{0}'".format(article_id))
            already_scraped = db_cursor.fetchone()[0]

            if not already_scraped:
                article_request = requests.get(article_url)

                # Some of the articles are just videos, ignore them
                if '/av/' not in article_request.url and '/sport/' not in article_request.url:
                    article_soup = BeautifulSoup(article_request.content, features='html5lib')

                    article_headline = article_soup.find('h1').get_text()

                    if article_soup.find('time') is None:
                        article_utc = article_soup.find('div', class_="date")['data-seconds']
                        article_date = time.strftime('%Y-%m-%d', time.localtime(int(article_utc)))
                    else:
                        article_date = article_soup.find('time')['datetime'][:10]
                                

                    if article_soup.find('div', class_='story-body__inner') is None:
                        article_inner = article_soup.find('article')
                    else:
                        article_inner = article_soup.find('div', class_='story-body__inner')

                    # Get rid of all the images and lists and whathaveyou
                    bad_tags = ['figure', 'ul', 'script', 'header', 'section', 'style']
                    for tag in bad_tags:
                        for element in article_inner.find_all(tag):
                            element.extract()

                    # Get rid of the prompt to add your own comments
                    bad_strings = ['haveyoursay@bbc.co.uk', 'if you are willing to speak to a bbc journalist']
                    for paragraph in article_inner.find_all('p'):
                        for string in bad_strings:
                            if string in paragraph.get_text().lower():
                                paragraph.extract()

                    article_body = article_inner.get_text().strip()


                    try:
                        db_cursor.execute('INSERT INTO articles (id, headline, body, date) VALUES (?,?,?,?)', (article_id, article_headline, article_body, article_date))
                        db.commit()
                        print("added {0}".format(article_headline))
                    except sqlite3.IntegrityError:
                        print('already added {0}'.format(article_headline))


        except Exception:
            print('{0}: {1}'.format(article_url, sys.exc_info()))
            logger.warning('[BBC@{0}] {1}: {2}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_url, sys.exc_info()))
            

db.close()

print('All done!')