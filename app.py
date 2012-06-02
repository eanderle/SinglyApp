import os
from pymaps import Map, PyMap, Icon # import the libraries
from flask import Flask, request, redirect, session
from flask import render_template
import requests

app = Flask(__name__)

SINGLY_CLIENT_ID = 'b4951689e26fe3cc15c2a940db08e7b7'
SINGLY_CLIENT_SECRET = '0e9aebaa610bd0e68cb2026934bfafbf'


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/signin-twitter')
def toAuth():
    url = 'https://api.singly.com/oauth/authorize?client_id=b4951689e26fe3cc15c2a940db08e7b7&redirect_uri=http://localhost:5000/callback&service=twitter'
    return redirect(url)

@app.route('/signin-facebook')
def authFacebook():
    url = 'https://api.singly.com/oauth/authorize?client_id=b4951689e26fe3cc15c2a940db08e7b7&redirect_uri=http://localhost:5000/callback&service=facebook'
    return redirect(url)

@app.route('/signin-foursquare')
def authFourSquare():
    url = 'https://api.singly.com/oauth/authorize?client_id=b4951689e26fe3cc15c2a940db08e7b7&redirect_uri=http://localhost:5000/callback&service=foursquare'
    return redirect(url)

@app.route('/signin-instagram')
def authInstagram():
    url = 'https://api.singly.com/oauth/authorize?client_id=b4951689e26fe3cc15c2a940db08e7b7&redirect_uri=http://localhost:5000/callback&service=instagram'
    return redirect(url)

@app.route('/callback')
def toAccess():
    code = request.args['code']
    postdata = {'client_id': SINGLY_CLIENT_ID, 'client_secret': SINGLY_CLIENT_SECRET, 'code': code}
    r = requests.post('https://api.singly.com/oauth/access_token', data=postdata)
    session['accesstoken'] = r.text
    return redirect('/')

app.secret_key = '\x01\xe9\xc9\xb2[\xf4l\xfc\xf0\x19\x98\xfc\x04+\xfb\x90\x14\x9f\x8e:z}\xce\t'

@app.route('/home', methods=['GET'])
def home():
	return render_template('home.html')

@app.route('/apitesting', methods=['GET', 'POST'])
def apitesting():
    if request.method == 'POST':
        f = request.form
        return str(session['accesstoken'])
        #return "form:{0} \n access_token_arg:{1} \n access_session: {2}".format(str(f), str(request.args['access_token']), str(session['accesstoken']))
        # if request.args['access_token']:
        #     access = request.args['access_token']
        # else:
        #     access = session['accesstoken']
        # rurl = "/types/all_feed?near={0},{1}&within={2}&access_token={3}".format(
        #     f.latitude,f.longitude, f.radius, access)
        # r = request.get(rurl)
        # return "<pre>{0}</pre>".format(str(r.text))
    elif request.method == 'GET':
        return render_template('apiTest.html')
    else:
        return "FAIL HARD"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
