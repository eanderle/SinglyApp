import os
from pymaps import Map, PyMap, Icon # import the libraries
from flask import Flask
from flask import render_template

app = Flask(__name__)

def getcords(d, m, s, ind):
    # Calculate the total number of seconds, 
    # 43'41" = (43*60 + 41) = 2621 seconds.

    sec = float((m * 60) + s)
    # The fractional part is total number of 
    # seconds divided by 3600. 2621 / 3600 = ~0.728056

    frac = float(sec / 3600)
    # Add fractional degrees to whole degrees 
    # to produce the final result: 87 + 0.728056 = 87.728056

    deg = float(d + frac)
    # If it is a West or S longitude coordinate, negate the result.
    if ind == 'W':
        deg = deg * -1

    if ind == 'S':
        deg = deg * -1

    return float(deg)

def showmap():
    # Create a map - pymaps allows multiple maps in an object
    icon = Icon()
    tmap = Map()
    tmap.zoom = 3

    # Latitude and lognitude - see the getcords function
    # to see how we convert from traditional D/M/S to the DD type
    # used by Googel Maps

    latitude = 0.0
    longitude = 0.0

    # These coordinates are for Hong Kong
    dlat = "22 15 0 N"
    dlong = "114 10 60 E"

    dlat = dlat.split()
    dlong = dlong.split()

    # Convert the coordinates
    latitude = getcords(float(dlat[0]), float(dlat[1]), float(dlat[2]), dlat[3])
    longitude = getcords(float(dlong[0]), float(dlong[1]), float(dlong[2]), dlong[3])

    # Inserts html into the hover effect
    pointhtml = "Hello!"

    # Add the point to the map
    point = (latitude, longitude, pointhtml, icon.id)

    tmap.setpoint(point)
    tmap.center = (1.757537,144.492188)

    # Put your own googl ekey here
    gmap = PyMap(key='AIzaSyBQY721WCNx1VXer7EdOVhCyMrF42iWq58', maplist=[tmap])
    gmap.addicon(icon)

    # pymapjs exports all the javascript required to build the map!
    mapcode = gmap.pymapjs()

    # Do what you want with it - pass it to the template or print it!
    return mapcode

@app.route('/')
def hello():
    return render_template('index.html') + showmap()

@app.route('/home', methods=['GET'])
def home():
	return render_template('home.html')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
