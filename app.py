from datetime import datetime, timedelta
import json
import nltk
import jwt

from flask import Flask, request, jsonify, abort
from nltk.corpus import stopwords
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
                jwt.decode(jwt_token,app.config["JWT_SECRET"] , app.config["JWT_ALGORITHM"])
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
def create_task():
    try:
        requestData = json.loads(request.data.decode('utf-8'))
    except:
        return jsonify({'message': 'Data is not provided'})
    if 'message' in requestData:
        message = requestData['message']
        tokenized_message = nltk.word_tokenize(message)
        filtered_words = [word for word in tokenized_message if word not in stopwords.words('english')]
        analyzed_words = TextBlob(message)
        if analyzed_words.sentiment.polarity >= .5:
            sentiment = "positive"
        elif analyzed_words.sentiment.polarity >= 0 and analyzed_words.sentiment.polarity < .5:
            sentiment = "neutral"
        else:
            sentiment = "negative"
        data = {
            "tokens":tokenized_message,
            "filtered":filtered_words,
            "POS":analyzed_words.tags,
            "sentiment":sentiment
        }
        return jsonify(data)
    else:
        return jsonify({'message': 'Data is not provided'})



@app.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        requestData=json.loads(request.data.decode('utf-8'))
    except:
        return jsonify({'message': 'App Id is not provided'})
    if 'appId'  in requestData:
        appId=requestData['appId']
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