from flask import Flask, render_template, request, jsonify, redirect, g, session, make_response
import sqlite3
import numpy
from datetime import datetime

from analysis import sentiment
import os

app = Flask(__name__)

analysed_data = []

class FormError(Exception):
    def __init__(self, fieldset, message):
        self.fieldset = fieldset
        self.message = message

# Singleton pattern for db from https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('compiled.sqlite')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/', methods=['GET'])
def showForm():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def processForm():
    global analysed_data

    # Get the variables in a try/except to allow for validation through FormError exceptions
    try:
        # Get all the data sources (every field name that starts with 'source')
        sources = [field[7:] for field in request.form.keys() if field.startswith('source')]
        if len(sources) == 0:
            raise FormError('source', 'Please select a source')

        period_full = 'period_full' in request.form
        if not period_full:
            try:
                period_start = datetime.strptime(request.form['period_start'], '%Y-%m-%d')
                period_end = datetime.strptime(request.form['period_end'], '%Y-%m-%d')
            except ValueError:
                # Can't convert to date (most likely empty string)
                raise FormError('period', 'Please specify a start and end date')

            if period_start >= period_end:
                raise FormError('period', 'Please specify a start date before the end date')
        
        data_resolution = int(request.form['data_resolution'])

    except FormError as e:
        error_message = e.message.replace(' ', '%20')
        return redirect(f'/?fieldset={e.fieldset}&message={error_message}')


    # Format everything into an SQL friendly format
    formatted_sources = "'{0}'".format("', '".join(sources))

    if period_full:
        formatted_period = ''
    else:
        formatted_period = f"AND articles.date BETWEEN '{period_start.strftime('%Y-%m-%d')}' AND {period_end.strftime('%Y-%m-%d')}"


    if data_resolution != '0':

        # This sql query was sourced from https://stackoverflow.com/questions/66302739/sql-query-to-select-records-with-altering-granularity
        sql_query = f"""
            WITH cte(date) AS (
                SELECT MIN(date) FROM articles
                UNION ALL
                SELECT date(date, '+{data_resolution} days')
                FROM cte
                WHERE date(date, '+{data_resolution} days') <= (SELECT MAX(date) FROM articles)
            )
            SELECT articles.* 
            FROM articles INNER JOIN cte
            ON cte.date = articles.date
            WHERE articles.source IN ({formatted_sources}) {formatted_period}
            GROUP BY articles.date"""

    else:
        # Construct the query
        sql_query = f"SELECT * FROM articles WHERE source IN ({formatted_sources}) {formatted_period}"


    query_result = query_db(sql_query)
    

    if request.form['analysis_method'] != 'none':
        
        if request.form['analysis_method'] == 'sentiment':

            analysed_data = {}

            # Calculate the analysis
            analysed_data['headline'] = {}
            analysed_data['body'] = {}
            for row in query_result:
                analysed_data['headline'][row[4]] = sentiment.analyse((row[2]))['compound']
                analysed_data['body'][row[4]] = sentiment.analyse((row[3]))['compound']


            return redirect('/')
    else:
        return 'no'


@app.route('/download')
def download():
    response = make_response(jsonify(analysed_data))
    response.headers["Content-Disposition"] = "attachment; filename=analysis.json"
    return response

@app.route('/data')
def data():
    return jsonify(analysed_data)
