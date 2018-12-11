from flask import Flask, render_template, send_from_directory, request
from flask_bootstrap import Bootstrap
from sentwiment import *

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    return app


app = create_app()


@app.route('/')
def index():
    tweets = twitter.user_timeline(screen_name="kanyewest", count=TWEET_COUNT, tweet_mode='extended')
    user = twitter.get_user("kanyewest").name
    usermood = "Kanye West"
    if len(tweets) == 0:
        return "No Tweets fo this user :("
    data = sentiment(tweets)
    if data['sentiment'] == -1:
        usermood += " sad"
    elif data['sentiment'] == 1:
        usermood += " happy"
    gif = get_gif(usermood)
    return render_template('index.html', twitter_data=data, sentiment=data["sentiment"],emotion=get_Mood(data["sentiment"]), user="kanyewest", gif=gif)


@app.route('/search', methods=['POST'])
def search():
    username = request.form['user']
    tweets = twitter.user_timeline(screen_name=username, count=TWEET_COUNT, tweet_mode='extended')
    user = twitter.get_user(username).name
    usermood = user
    if len(tweets) == 0:
        return "No Tweets fo this user :("
    data = sentiment(tweets)
    if data['sentiment'] == -1:
        usermood += " sad"
    elif data['sentiment'] == 1:
        usermood += " happy"
    gif = get_gif(usermood)
    return render_template('index.html', twitter_data=data, sentiment=data["sentiment"],emotion=get_Mood(data["sentiment"]), user=username, gif=gif)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',mimetype='image/vnd.microsoft.icon')



if __name__ == "__main__":
    app.run()