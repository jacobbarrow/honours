import requests
import time
from datetime import date, timedelta, datetime
import re
import sqlite3
import logging
import sys
import hashlib

from bs4 import BeautifulSoup

TIME_BETWEEN_REQUESTS = 30 # Don't want to spam, so give some breathing space (seconds)
START_DATE = date(2011, 2, 4)
END_DATE = date(2020, 1, 1)


## Used to iterate through days in a range
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)


logger = logging.getLogger('independent-archive')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('independent-archive.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

	
# Set up database
db = sqlite3.connect('independent-archive.sqlite')
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

# Have to pass through a user agent, otherwise it 404s
user_agent_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

for dt in daterange(START_DATE, END_DATE):
    article_date = dt.strftime("%Y-%m-%d")

    listing_request = requests.get('https://www.independent.co.uk/archive/{0}'.format(article_date), headers=user_agent_header)
    if listing_request.status_code == 405:
        print("Blocked...")
        logger.debug('[{0}] Blocked (up to {1})'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_date))

        break


    listing_soup = BeautifulSoup(listing_request.content, features='html5lib')
    last_headline = None
    for li_tag in listing_soup.find('div', id="frameInner").find('ul').find_all('li'):
        article_url = li_tag.find('a')['href']
        article_headline = li_tag.find('a').get_text()

        try:
            # A lot of duplicates pop up, so catch them before checking database
            if '/news/' in article_url and article_headline != last_headline:
                last_headline = article_headline

                article_id = hashlib.md5(article_url.encode('utf-8')).hexdigest()
                db_cursor.execute("SELECT Count() FROM articles WHERE id='{0}'".format(article_id))
                already_scraped = db_cursor.fetchone()[0]

                if not already_scraped:
                    article_request = requests.get("https://www.independent.co.uk{0}".format(article_url), headers=user_agent_header)
                    article_soup = BeautifulSoup(article_request.content, features='lxml')

                    article_inner = article_soup.find('div', class_="body-content")

                    if article_inner is None:
                        article_inner = article_soup.find('div', id='main')


                    article_body = ""
                    for p in article_inner.find_all('p'):
                        p_text = p.get_text()
                        if not p_text.startswith('@'):
                            article_body += '{0}\n'.format(p_text.strip())  
                    
                    try:
                        db_cursor.execute('INSERT INTO articles (id, headline, body, date) VALUES (?,?,?,?)', (article_id, article_headline, article_body, article_date))
                        db.commit()
                        print("added {0}".format(article_headline[:30]))
                    except sqlite3.IntegrityError:
                        print('already added {0}'.format(article_headline))
        
                    time.sleep(TIME_BETWEEN_REQUESTS)


        
        except Exception:
            print('{0}: {1}'.format(article_url, sys.exc_info()))
            logger.warning('[{0}] {1}: {2}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_url, sys.exc_info()))
                
    logger.debug('[{0}] Finished scraping {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), article_date))


db.close()

print('All done!')