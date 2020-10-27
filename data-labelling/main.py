from flask import Flask, url_for, render_template, request, redirect
import ratings

app = Flask(__name__, template_folder='views')

@app.route('/')
def showDisclaimer():
    return render_template('disclaimer.html')

@app.route('/rating', methods=['GET'])
def showRating():
    article = ratings.getLeastRatedArticle()
    return render_template('rating.html', article=article)

@app.route('/rating', methods=['POST'])
def submitRating():
    time_taken = request.form['time_taken']
    rating = request.form['rating']
    article_id = request.form['article_id']

    ratings.add(article_id, rating, time_taken)
    
    return redirect(url_for('showRating'))


if __name__ == '__main__':
    app.run(debug=True)