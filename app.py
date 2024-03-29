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

def grab_singly_data(latitude, longitude, radius):
    rurl = "/types/all_feed?near={0},{1}&within={2}".format( latitude, longitude, radius)
    r = requests.get(api_call(rurl))
    return json.loads(r.text)

def grab_twitter_data(lat, longitude, rad):
    data = []
    rurl = "https://search.twitter.com/search.json?q=since:2012-05-15&geocode={0},{1},{2}km&rpp=100&page=".format(lat,longitude, rad)
    print "OMGURL========\n\n\n {0}\n\n\ =========".format(rurl)
    for i in range(1,10):
        r = requests.get(rurl+str(i))
        Jresponse = r.text
        newData = json.loads(Jresponse)
        data.append(newData)
    return data

# returns a generator of strings representing
# posts, tweets, etc within a radius of coords
def get_by_loc(coord, radius):
    latitude = str(coord[0])
    longitude = str(coord[1])
    radius = str(radius)
    singlyData = grab_singly_data(latitude, longitude, radius)
    twitterData = grab_twitter_data(latitude, longitude, radius)
    return singlyData.append(twitterData)

# returns the result of sentiment analysis on
# a given string s
def analyze_sentiment(s):
    return random.randint(LOWEST_SENTIMENT,HIGHEST_SENTIMENT)

def api_call(url, access_token=None):
    """Takes the url and appends the singly api url and access_token"""
    if access_token:
        tok = access_token
    elif not access_token and 'accesstoken' in session:
        tok = session['accesstoken']
    elif not access_token and 'accesstoken' not in session:
        return "FAIL HARD"

    if '?' in url: #includes some parameters
        return "{0}{1}&access_token={2}".format(SINGLY_API_URL, url, tok)
    else:
        return "{0}{1}?access_token={2}".format(SINGLY_API_URL, url, tok)


def calc_squares(start_lat, start_long, chunks, size):
    squares = []
    for i in range(-1*(chunks/2), (chunks/2)):
        for j in range(-1*(chunks/2), (chunks/2)):
            lat = start_lat + (size * i)
            lng = start_long + (size * j)
            square_mean = RunningMean()
            center = ((start_lat+(i+1))/2, (start_long+(j+1))/2)
            updates = get_by_loc(center, size/2)
            for update in updates:
                square_mean.push(analyze_sentiment(update))
            opacity = (square_mean.mean - LOWEST_SENTIMENT) / (HIGHEST_SENTIMENT - LOWEST_SENTIMENT)
            squares.append((lat, lng, opacity))
    return squares

@app.route('/map')
def map():
    if 'accesstoken' in session:
        start_lat = 37.7750
        start_long = -122.4183
        chunks = 30
        size = .005
        squares = calc_squares(start_lat, start_long, chunks, size)
        return render_template('index.html', squares=squares, chunks=chunks)
    else:
        return redirect('/signin-facebook')

@app.route('/')
def hello():
    if 'accesstoken' in session:
        return redirect('/home')
    else:
        return redirect('/signup')

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
    data = []
    for i in range(1,10):
        r = requests.get('https://search.twitter.com/search.json?q=since:2012-05-15&geocode=37.781157,-122.398720,10km&rpp=100&page='+str(i))
        Jresponse = r.text
        newData = json.loads(Jresponse)
        data.append(newData)

    jt = json.dumps(data, indent=2 * ' ')
    twittertxt = '\n'.join([l.rstrip() for l in jt.splitlines()])
    return "<pre>{0}</pre>".format(twittertxt)

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
        f = {}
        for (k,v) in request.form.iteritems():
            f[k] = v.strip()
        singlyData = grab_singly_data(f['latitude'], f['longitude'], f['radius'])
        twitterData = grab_twitter_data(f['latitude'], f['longitude'], f['radius'])
        js = json.dumps(singlyData, indent=2 * ' ')
        singlytxt = '\n'.join([l.rstrip() for l in  js.splitlines()])
        jt = json.dumps(twitterData, indent=2 * ' ')
        twittertxt = '\n'.join([l.rstrip() for l in jt.splitlines()])
        return "<h3>Singly Data</h3><pre>{0}\n\n\n</pre><h3>Twitter Data</h3><pre>{1}</pre>".format(singlytxt, twittertxt)
    elif request.method == 'GET':
        return render_template('apiTest.html')
    else:
        return "FAIL HARD"

@app.route('/apiexplorer', methods=['GET', 'POST'])
def apiexplorer():
    if request.method == 'POST':
        f = request.form
        if f['access_token']:
            rurl = api_call(f['url'], f['access_token'])
        else:
            rurl = api_call(f['url'])
        r = requests.get(rurl)
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
