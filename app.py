from datetime import datetime, timedelta
import json
import nltk
import jwt

from flask import Flask, request, jsonify, abort
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from registeredAppList import CLIENT_APP_IDS



app = Flask(__name__)
app.config.from_object('config')

def authenticate_api(func):
    """ Authenticate api calls based on token"""
    def authenticate_and_call(*args, **kwargs):
        jwt_token = request.headers.get('authorization', None)
        if jwt_token:
            try:
                jwt.decode(jwt_token,app.config["JWT_SECRET"], app.config["JWT_ALGORITHM"])
                return func(*args, **kwargs)
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                abort(401)
        else:
            abort(401)

    return authenticate_and_call


@app.route('/')
def index():
     return "API for text Processing"


@app.route('/processMessage', methods=['POST'])
@authenticate_api
def process_message():
    """ Process message and find sentiments"""
    try:
        requestData = json.loads(request.data.decode('utf-8'))
    except:
        return jsonify({'message': 'Data is not provided'})
    if 'message' in requestData:
        message = requestData['message']
        sid = SentimentIntensityAnalyzer()
        vad_score = sid.polarity_scores(message)
        neg_score = vad_score['neg']
        pos_score = vad_score['pos']
        neu_score = vad_score['neu']
        if neg_score > pos_score and neg_score > neu_score:
            vad_sentiment = 'negative'
        elif pos_score > neg_score and pos_score > neu_score:
            vad_sentiment = 'positive'
        else:
            vad_sentiment = 'neutral'
        tokenized_message = nltk.word_tokenize(message)
        filtered_words = [word for word in tokenized_message if word not in stopwords.words('english')]
        analyzed_words = TextBlob(message)
        if analyzed_words.sentiment.polarity > .5:
            sentiment = "positive"
        elif analyzed_words.sentiment.polarity >= 0 and analyzed_words.sentiment.polarity <= .5:
            sentiment = "neutral"
        else:
            sentiment = "negative"
        data = {
            "keywords":filtered_words,
            "sentiment":sentiment,
            "vader_sentiment":vad_sentiment
        }
        return jsonify(data)
    else:
        return jsonify({'message': 'Data is not provided'})



@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Issues JWT token for API calls"""
    try:
        requestData=json.loads(request.data.decode('utf-8'))
    except:
        return jsonify({'message': 'App Id is not provided'})
    if 'appId'  in requestData:
        appId = requestData['appId']
    else:
        return jsonify({'message': 'App Id is not provided'})
    if appId in CLIENT_APP_IDS:
        payload = {
            'appId': appId,
            'exp': datetime.utcnow() + timedelta(seconds=app.config["JWT_EXP_DELTA_SECONDS"])
        }
        jwt_token = jwt.encode(payload, app.config["JWT_SECRET"], app.config["JWT_ALGORITHM"])
        return jsonify({'token': jwt_token.decode('utf-8')})
    else:
        abort(401)





if __name__ == '__main__':
    app.run()