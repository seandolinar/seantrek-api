#!flask/bin/python
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import datetime


app = Flask(__name__)
# app.run(threaded=True)

# app.json_encoder = CustomJSONEncoder

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = SQLAlchemy(app)

results = db.engine.execute("select * from trip_main;")

def getTrips(state_id = 0):
    
    dataTrips = []

    sql_state = 'SELECT a.* \
        FROM trip_main a \
        LEFT JOIN trip_state b \
        ON (a.trip_id = b.trip_id) \
        WHERE b.state_id IN (' + str(state_id) + ') \
        GROUP BY a.date_start, b.trip_id'

    trips = dbConn()
    trips.sqlString = sql_state if state_id != 0 else 'select * from trip_main order by date_start;'
    trips = trips.getQuery()
    
    photos = dbConn()
    photos.sqlString = 'select * from trip_photos;'
    photos = photos.getQuery()

    for trip in trips:

        # cleans up dictionary for API return
        dictTrip = trip


        dataPhotos = []

        for photo in photos:
            dictPhoto = photo

            if dictPhoto['trip_id'] == dictTrip['trip_id']:
                dataPhotos.append(dictPhoto)

        dictTrip['photos'] = dataPhotos
        dataTrips.append(dictTrip)

    return dataTrips

def getOneTrip(name):

    id = 0

    for trip in static_trips:
        if trip['trip_label'].lower().replace(' ', '-') == name:
            id = trip['trip_id']

    trip = dbConn()
    trip.sqlString = 'select * from trip_main where trip_id=' + str(id) + ' order by date_start limit 1;'
    trip = trip.getQuery()

    states = dbConn()
    states.sqlString = ('select b.abbreviation, b.name, b.id from trip_state a' +
        ' left join ref_state b on (a.state_id=b.id)' + 
        'where trip_id=' + str(id))
    states = states.getQuery()

    if len(trip) > 0:
        trip[0]['states'] = states

    presidents = dbConn()
    presidents.sqlString = ('select * from trip_presidents a' +
        ' left join ref_presidents b on (a.president_id=b.president_id)' + 
        'where trip_id=' + str(id))
    presidents = presidents.getQuery()

    if len(trip) > 0:
        trip[0]['presidents'] = presidents


    return trip

def getState(stateCode):
    state_id = 0

    for state in static_states:
       if state['abbreviation'].lower() == stateCode.lower():
            state_id = state['id'] 

    return getTrips(state_id)

class dbConn(object):
    sqlString = ''

    def getQuery(self):
        arrOut = []
        dictOut = {}
        results = db.engine.execute(self.sqlString)

        keys = results.keys()
        for row in results:
            dictOut = {}
            for key in keys:
                if type(row[key]) is datetime.date:
                    dictOut[key] = row[key].isoformat()
                else:
                    dictOut[key] = row[key]

            arrOut.append(dictOut)

        return arrOut

def staticStates():

    states = dbConn()
    states.sqlString = ('select b.abbreviation, b.name, b.id from ref_state b')
    states = states.getQuery()

    return states

static_trips = getTrips()
static_states = staticStates()



@app.route('/api/trips', methods=['GET'])
def get_tasks():
    return jsonify(getTrips())

@app.route('/api/tripone/<string:name>', methods=['GET'])
def get_trip(name):
    return jsonify(getOneTrip(name))

@app.route('/api/state/<string:state>', methods=['GET'])
def get_state(state):
    return jsonify(getState(state))

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
