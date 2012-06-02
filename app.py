import os
from pymaps import Map, PyMap, Icon # import the libraries
from flask import Flask, request, redirect, session, jsonify
from flask import render_template
import requests
import simplejson as json
import random


app = Flask(__name__)

SINGLY_CLIENT_ID = 'b4951689e26fe3cc15c2a940db08e7b7'
SINGLY_CLIENT_SECRET = '0e9aebaa610bd0e68cb2026934bfafbf'
SINGLY_API_URL = 'https://api.singly.com/v0'
app.secret_key = '\x01\xe9\xc9\xb2[\xf4l\xfc\xf0\x19\x98\xfc\x04+\xfb\x90\x14\x9f\x8e:z}\xce\t'

LOWEST_SENTIMENT = 0
HIGHEST_SENTIMENT = 100

# Compute running mean
# http://www.johndcook.com/standard_deviation.html
class RunningMean(object):
	var_sum = 0
	maximum = 0
	num_entries = 0
	mean = 0

	def push(self, x):
		self.num_entries += 1
		if x > self.maximum:
			self.maximum = x
		if self.num_entries == 1:
			self.mean = float(x)
		else:
			old_mean = self.mean
			old_var_sum = self.var_sum
			self.mean = old_mean + ((x - old_mean) / self.num_entries)
			self.var_sum = old_var_sum + ((x - old_mean) * (x - self.mean))
	
	def std_dev(self):
		return sqrt(self.var_sum / (self.num_entries - 1)) if self.num_entries > 1 else 0

# returns a generator of strings representing
# posts, tweets, etc within a radius of coords
def get_by_loc(coords, radius):
    for i in range(100):
        yield 'sup bro'

# returns the result of sentiment analysis on
# a given string s
def analyze_sentiment(s):
    sentiment = random.randint(LOWEST_SENTIMENT,HIGHEST_SENTIMENT)
    print 'sentiment: ' + str(sentiment)
    return sentiment

def api_call(url):
    """Takes the url and appends the singly api url"""
    return "{0}{1}".format(SINGLY_API_URL, url)

def calc_squares(start_lat, start_long, chunks, size):
    for i in range(-1*(chunks/2), (chunks/2)):
        for j in range(-1*(chunks/2), (chunks/2)):
            square_mean = RunningMean()
            center = ((start_lat+(i+1))/2, (start_long+(j+1))/2)
            updates = get_by_loc(center, size/2)
            for update in updates:
                square_mean.push(analyze_sentiment(update))
            opacity = (square_mean.mean - LOWEST_SENTIMENT) / (HIGHEST_SENTIMENT - LOWEST_SENTIMENT)
            print 'opacity: ' + str(opacity)

@app.route('/')
def hello():
    if 'accesstoken' in session:
        return redirect('/home')
    else:
        calc_squares(0, 0, 30, .005)
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

@app.route('/testauth')
def testAuth():
    return session['accesstoken']

@app.route('/teststream')
def testStream():
    r = requests.post('https://stream.twitter.com/1/statuses/filter.json',
    data={'track': 'requests'}, auth=('username', 'password'))
    counter = 1;
    for line in r.iter_lines():
        counter = counter + 1
        if line: # filter out keep-alive new lines
            if counter < 3:
                print json.loads(line)
            else:
                return "Done"

@app.route('/callback')
def toAccess():
    code = request.args['code']
    postdata = {'client_id': SINGLY_CLIENT_ID, 'client_secret': SINGLY_CLIENT_SECRET, 'code': code}
    r = requests.post('https://api.singly.com/oauth/access_token', data=postdata)
    Jresponse = r.text
    data = json.loads(Jresponse)
    session['accesstoken'] = data['access_token']
    return redirect('/home')

@app.route('/clearsession')
def clearsession():
    session.pop('accesstoken', None)
    return "Done"


@app.route('/home', methods=['GET', 'POST'])
def home():
	if 'accesstoken' in session:
		if request.method == 'GET':
			return render_template('home.html')
		elif request.method == 'POST':
			return render_template('home.html')
		else:
			return "woah woah woah! What http request did you just make!?"
	else:
		return redirect('/')

@app.route('/apitesting', methods=['GET', 'POST'])
def apitesting():
    if request.method == 'POST':
        f = request.form
        if 'accesstoken' in session:
            access = session['accesstoken']
        else:
            access = 'fake'
        rurl = "/types/all_feed?near={0},{1}&within={2}&access_token={3}".format(
            f['latitude'],f['longitude'], f['radius'], access)
        r = requests.get(api_call(rurl))
        j1 = json.dumps(json.loads(r.text), indent=4 * ' ')
        text = '\n'.join([l.rstrip() for l in  j1.splitlines()])
        return "<pre>{0}</pre>".format(text)
    elif request.method == 'GET':
        return render_template('apiTest.html')
    else:
        return "FAIL HARD"

@app.route('/apiexplorer', methods=['GET', 'POST'])
def apiexplorer():
    def add_access_tok(url, access_token):
        if "?" in url:
            return "{0}&access_token={1}".format(url, access_token)
        else:
            return "{0}?access_token={1}".format(url, access_token)

    if request.method == 'POST':
        f = request.form
        if f['access_token']:
            rurl = add_access_tok(f['url'], f['access_token'])
        else:
            rurl = add_access_tok(f['url'], session['accesstoken'])
        r = requests.get(api_call(rurl))
        j1 = json.dumps(json.loads(r.text), indent=4 * ' ')
        text = '\n'.join([l.rstrip() for l in  j1.splitlines()])
        return "<pre>{0}</pre>".format(text)
    elif request.method == 'GET':
        return render_template('apiexplore.html')
    else:
        return "FAIL HARD"


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
