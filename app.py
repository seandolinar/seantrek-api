#!flask/bin/python
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import datetime
import os

app = Flask(__name__)

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = SQLAlchemy(app)

results = db.engine.execute("select * from trip_main;")

def getStateCount():

    stateCount = dbConn()
    stateCount.sqlString = "SELECT state_id, count(*) as count, \
            case \
            when count(*) = 1 then 'ONE' \
            when count(*) = 2 then 'TWO' \
            when count(*) = 3 then 'THREE' \
            else 'FIVE' \
            end as number, b.abbreviation AS id \
            FROM trip_state a \
            LEFT JOIN ref_state b \
            ON (a.state_id = b.id) \
            GROUP BY state_id, b.id"
    stateCount = stateCount.getQuery()

    dictOut = {}

    for state in stateCount:
        dictOut[state['id']] = {"fillKey": state['number']}

    return dictOut


def getTrips(state_id = 0, featured=False):
    
    dataTrips = []

    sql_state = 'SELECT a.* \
        FROM trip_main a \
        LEFT JOIN trip_state b \
        ON (a.trip_id = b.trip_id) \
        WHERE b.state_id IN (' + str(state_id) + ') \
        GROUP BY a.date_start, b.trip_id'

    trips = dbConn()
    trips.sqlString = sql_state if state_id != 0 else 'select * from trip_main order by date_start;'
    trips.sqlString = trips.sqlString if not featured else 'select * from trip_main where trip_featured != 0 order by trip_featured;'
    trips = trips.getQuery()
    
    photos = dbConn()
    photos.sqlString = 'select * from trip_photos where featured != 0 order by featured;'
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
    trip.sqlString = 'select *, to_char(date_start, \'Mon FMDD, YYYY\') as date_start_display, to_char(date_end, \'Mon FMDD, YYYY\') as date_end_display from trip_main where trip_id=' + str(id) + ' order by date_start limit 1;'
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

    photos = dbConn()
    photos.sqlString = 'select * from trip_photos where featured != 0 order by featured;'
    photos = photos.getQuery()

    dataPhotos = []

    for photo in photos:
        dictPhoto = photo

        if dictPhoto['trip_id'] == trip[0]['trip_id']:
            dataPhotos.append(dictPhoto)

    trip[0]['photos'] = dataPhotos


    return trip

def getState(stateCode):
    state_id = 0

    for state in static_states:
       if state['abbreviation'].lower() == stateCode.lower():
            state_id = state['id'] 

    return getTrips(state_id)

def getPresident(number):
    presidents = dbConn()
    presidents.sqlString = ('select * from ref_presidents ' + 
        'where number=' + str(number))
    presidents = presidents.getQuery()

    return presidents

def getPhotoGrid():

    categories = ['N', 'C', 'F', 'H']
    arrSQL = []

    for category in categories:
        arrSQL.append("(SELECT *, RANDOM() FROM trip_photos WHERE photo_type = '" + category + "' ORDER BY RANDOM DESC LIMIT 5)")

    strSQL = ('UNION').join(arrSQL)

    strSQL = 'SELECT a.*, b.trip_label FROM (' + strSQL + ') a \
            LEFT JOIN trip_main b \
            ON (a.trip_id = b.trip_id)'

    photos = dbConn()
    photos.sqlString = strSQL
    photos = photos.getQuery()

    return photos

def getPhoto(photo_id):
    photo = dbConn()
    photo.sqlString = 'select a.*, b.trip_label from trip_photos a \
        LEFT JOIN trip_main b \
        ON (a.trip_id = b.trip_id) \
        where photo_id=' + str(photo_id) + ' limit 1;'
    photo = photo.getQuery()

    return photo


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
    return jsonify(getTrips(featured=False))

@app.route('/api/trips-featured', methods=['GET'])
def get_trips_featured():
    return jsonify(getTrips(featured=True))

@app.route('/api/tripone/<string:name>', methods=['GET'])
def get_trip(name):
    return jsonify(getOneTrip(name))

@app.route('/api/state/<string:state>', methods=['GET'])
def get_state(state):
    return jsonify(getState(state))

@app.route('/api/state-count', methods=['GET'])
def get_state_count():
    return jsonify(getStateCount())

@app.route('/api/president/<string:president>', methods=['GET'])
def get_president(president):
    return jsonify(getPresident(president))

@app.route('/api/photo-grid', methods=['GET'])
def get_photo_grid():
    return jsonify(getPhotoGrid())

@app.route('/api/photos/<string:photo_id>', methods=['GET'])
def get_photo(photo_id):
    return jsonify(getPhoto(photo_id))






if __name__ == '__main__':
    # app.run(debug=True, threaded=True)
    app.debug = True
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
