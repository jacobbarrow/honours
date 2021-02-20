import sqlite3, os

SOURCES = {
    'bbc-a': 'bbc-on-this-day',
    'bbc-d': 'bbc-daily',
    'gua-d': 'guardian-daily',
    'huf-d': 'huffpost-daily',
    #'ind-a': 'independent-archive',
    'mai-d': 'mail-daily'
}

# Set up database
try:
    os.remove('compiled.sqlite')
except OSError:
    pass


compiled_db = sqlite3.connect('compiled.sqlite')
compiled_db_cursor = compiled_db.cursor()

create_table_sql = """
CREATE TABLE articles(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   source TEXT,
   headline TEXT,
   body TEXT,
   date TEXT
);
"""
try:
    compiled_db_cursor.execute("SELECT * FROM articles")
except sqlite3.OperationalError:
    compiled_db_cursor.execute(create_table_sql)


for source_name, source_file in SOURCES.items():
    print(f"Adding {source_name}")
    source_db = sqlite3.connect(f'{source_file}.sqlite')
    source_db_cursor = source_db.cursor()
    for record in source_db_cursor.execute("SELECT * FROM articles"):
        parameters = (source_name, record[1], record[2], record[3])
        compiled_db_cursor.execute(f"INSERT INTO articles (source, headline, body, date) VALUES (?, ?, ?, ?)", parameters)
    source_db.commit()
    source_db.close()
    
compiled_db.commit()
compiled_db.close()

