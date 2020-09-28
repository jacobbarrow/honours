import requests
import time
import re
import sqlite3
from bs4 import BeautifulSoup

# Set up database
db = sqlite3.connect('bbc-on-this-day.sqlite')
db_cursor = db.cursor()

create_table_sql = """
CREATE TABLE articles(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   headline TEXT,
   body TEXT,
   date TEXT
);
"""
try:
    db_cursor.execute("SELECT * FROM articles")
except sqlite3.OperationalError:
    db_cursor.execute(create_table_sql)



# Used to convert month string to int
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

for year in range(1950, 2006):
    print("Adding {0}...".format(year))

    year_request = requests.get('http://news.bbc.co.uk/onthisday/hi/years/{0}/default.stm'.format(year))
    year_soup = BeautifulSoup(year_request.content, features='html5lib')

    for article_listing in year_soup.find('div', class_='bodytext').find('table').find_all('a'):
        article_url = article_listing['href']
        split_url = article_url.split('/')

        if split_url[4] == 'stories':

            article_request = requests.get('http://news.bbc.co.uk{0}'.format(article_url))
            article_soup = BeautifulSoup(article_request.content, features='html.parser')

            # Extract the month and day from the url
            month = months.index(split_url[5]) + 1
            day = int(split_url[6])
            article_date = '{0}-{1:02d}-{2:02d}'.format(year, month, day)

            article_soup = BeautifulSoup(article_request.content, features='html5lib')
            article_headline = article_soup.find('div', class_='hpad').find('b').contents[0][6:]


            article_body_soup = article_soup.find('div', class_='bodytext')

            # Remove all the tables
            for table in article_body_soup.find_all('table'):
                table.extract()

            # Remove the headline
            article_body_soup.find('font', {'size': '3'}).extract()

            # Remove all the tags and blank lines
            lines = article_body_soup.get_text().split('\n')
            article_body = '\n'.join([line.strip() for line in lines if line.strip() not in ['', '\t']])


            db_cursor.execute('INSERT INTO articles (headline, body, date) VALUES (?,?,?)', (article_headline, article_body, article_date))
            print("added {0}".format(article_headline))
            db.commit()
        
        else:
            print('skipping {0} ({1})'.format(article_url, split_url[4]))

db.close()