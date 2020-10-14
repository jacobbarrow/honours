from flask import Flask, url_for, render_template, request

app = Flask(__name__, template_folder='views')

@app.route('/')
def showDisclaimer():
    return render_template('disclaimer.html')

@app.route('/rating', methods=['GET'])
def showRating():
    return render_template('rating.html')

@app.route('/rating', methods=['POST'])
def submitRating():
    time_taken = request.form['time_taken']
    rating = request.form['rating']
    article_id = request.form['article_id']
    return '<p>{0}</p><p>{1}</p><p>{2}</p>'.format(time_taken, rating, article_id)
    

if __name__ == '__main__':
    app.run(debug=True)