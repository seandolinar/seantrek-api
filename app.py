#!flask/bin/python
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import datetime




app = Flask(__name__)
# app.json_encoder = CustomJSONEncoder

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = SQLAlchemy(app)

results = db.engine.execute("select * from trip_main;")

# for rec in results:
#     print rec.__dict__

class TripMain(db.Model):
    date_start = db.Column(db.String(20), primary_key=True)
    date_end = db.Column(db.String(20))
    trip_id = db.Column(db.Integer, unique=True)
    trip_label = db.Column(db.String(200))
    trip_desc = db.Column(db.String(1000))

    # photo_id = db.Column(db.Integer, db.ForeginKey('TripPhotos.photo_id'))
    # photo_name = db.relationship('TripPhotos',backref=db.backref('trip_main', lazy=True))



class TripPhotos(db.Model):
    photo_id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer)
    photo_name = db.Column(db.String)


def getTrips():
    
    dataTrips = []

    trips = dbConn()
    trips.sqlString = 'select * from trip_main;'
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

results = db.engine.execute("select * from trip_main;")


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


a = dbConn()
a.sqlString="select * from trip_main;"
a.getQuery()



@app.route('/api/trips', methods=['GET'])
def get_tasks():
    return jsonify(getTrips())

if __name__ == '__main__':
    app.run(debug=True)