import os
from pymaps import Map, PyMap, Icon # import the libraries
from flask import Flask, request
from flask import render_template
import requests

app = Flask(__name__)

SINGLY_CLIENT_ID = 'b4951689e26fe3cc15c2a940db08e7b7'
SINGLY_CLIENT_SECRET = '0e9aebaa610bd0e68cb2026934bfafbf'


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/signin')
def toAuth():
    url = 'https://api.singly.com/oauth/authorize?client_id=131cb07e5d121ab1fe152&redirect_uri=http://app.com/callback&service=twitter'

@app.route('/callback')
def toAccess():
    code = request.args['code']
    postdata = {'client_id': SINGLY_CLIENT_ID, 'client_secret': SINGLY_CLIENT_SECRET, 'code': code}
    r = requests.post('https://api.singly.com/oauth/access_token', data=postdata)
    return r.text

@app.route('/apitesting', methods=['GET', 'POST'])
def apitesting():
    if request.method == 'POST':
        f = request.form
        rurl = "/types/all_feed?near={0},{1}&within={2}&access_token={3}".format(
            f.latitude,f.longitude, f.radius, session['accesskey'])
    elif request.method == 'GET':
        return render_template('apiTest.html')
    else:
        return "FAIL HARD"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
