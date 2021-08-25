from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processUserInfo/<string:userInfo>', methods=['POST'])
def processUserInfo(userInfo):
    userInfo = json.loads(userInfo)
    print('USER INFO RECVEID')
    print('-----------------')
    print(f"User Name: {userInfo['name']}")

    return 'Info Recived Sucessely'

if __name__== "__main__":
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'), 
        port=int(os.getenv('PORT', 5000)))