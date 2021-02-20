from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.wrappers import Request
from datetime import datetime

app = Flask(__name__)

class FormError(Exception):
    def __init__(self, fieldset, message):
        self.fieldset = fieldset
        self.message = message

@app.route('/', methods=['GET'])
def showForm():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def processForm():

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

    except FormError as e:
        error_message = e.message.replace(' ', '%20')
        return redirect(f'/?fieldset={e.fieldset}&message={error_message}')


    # Format everything into an SQL friendly format
    formatted_sources = "'{0}'".format("', '".join(sources))

    if period_full:
        formatted_period = ''
    else:
        formatted_period = f"AND date BETWEEN '{period_start.strftime('%Y-%m-%d')}' AND {period_end.strftime('%Y-%m-%d')}"

    # Construct the query
    sql_query = f"SELECT * FROM db WHERE source IN ({formatted_sources}) {formatted_period}"

    return jsonify(sql_query)

