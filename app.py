#!/usr/bin/env python
# coding: utf-8


import numpy as np



import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



from flask import Flask, jsonify



# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect on existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



#Flask Setup
app = Flask(__name__)



# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes"""
    return(
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end><br/>"
    )


# since the question asks for these results to be "based on the queries 
# you just developed", this uses the station with the most observations 
# as per the most recent query. This eliminates the confusion that would
# be caused by having multiple precipitation entries for a single day
# (there is no place to specify which station the data came from).

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.station == "USC00519281").all()
    session.close()
    
    precip_data = []
    for date, prcp in data:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = prcp
        precip_data.append(precip_dict)
        
    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    data = session.query(Station).all()
    session.close()
    
    station_data = []
    for id, station, name, latitude, longitude, elevation in data:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        station_data.append(station_dict)
    
    return jsonify(station_data)



@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    max_date_station_result = session.query(func.max(Measurement.date)).filter(Measurement.station == 'USC00519281').first()
    max_date_station = datetime.strptime(max_date_station_result[0], '%Y-%m-%d')

    # Calculate the date 1 year ago from the last data point in the database
    min_date_station = max_date_station - dt.timedelta(days=366)
    min_date_station_string = datetime.strftime(min_date_station, "%Y-%m-%d") 
    most_observations_df = pd.read_sql("SELECT date, tobs FROM Measurement WHERE station = 'USC00519281' AND date > '" + min_date_station_string + "'", conn)

    most_observations_df = most_observations_df.sort_values('date')
   
    session.close()
    
    return most_observations_df.to_json()



@app.route("/api/v1.0/<start>")
def from_date(start):
    session = Session(engine)
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    
    temp_dict = {}
    for entry in data:
        temp_dict["TMIN"] = entry[0]
        temp_dict["TAVG"] = entry[1]
        temp_dict["TMAX"] = entry[2]
          
    return jsonify(temp_dict)


@app.route("/api/v1.0/<start>/<end>")
def between_date(start,end):
    session = Session(engine)
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start AND Measurement.date <= end).all()
    session.close()
    
    temp_dict = {}
    for entry in data:
        temp_dict["TMIN"] = entry[0]
        temp_dict["TAVG"] = entry[1]
        temp_dict["TMAX"] = entry[2]
          
    return jsonify(temp_dict)



if __name__ == '__main__':
    app.run(debug=True)

