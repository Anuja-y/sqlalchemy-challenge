from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import numpy as np
import pandas as pd
import datetime as dt


engine = create_engine("sqlite:///../Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station
session = Session(engine)

# Create an app
app = Flask(__name__)

# Homepage
@app.route('/')

def homepage():
    #Listing all the available routes.
    return(
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"  
        f"/api/v1.0/<start> <br/>" 
        f"/api/v1.0/<start>/<end> <br/>"

    )

# Precipitation
@app.route('/api/v1.0/precipitation')

def precipitation():
    #Convert the query results to a dictionary by using date as the key and prcp as the value.
    results_dict = {}
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= prev_year).all()

    for date, prcp in results:
        results_dict[date] = prcp

    #Return the JSON representation of your dictionary.
    return jsonify(results_dict)

# Stations
@app.route('/api/v1.0/stations')

def stations():
    station_q = session.query(Stations.id, Stations.station, Stations.name, Stations.latitude, Stations.longitude, Stations.elevation).all()
    station_list = []
    for id, station, name, latitude, longitude, elevation in station_q:
        station_list += id, station, name, latitude, longitude, elevation
    #Return a JSON list of stations from the dataset.
    return jsonify(station_list)


# Temperature
@app.route('/api/v1.0/tobs')

def temperature():

    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_dict = {}

    #Query the dates and temperature observations of the most-active station for the previous year of data.
    temp = session.query(Measurements.date, Measurements.tobs).filter(Measurements.station == 'USC00519281').filter(Measurements.date >= prev_year).all()
    
    #Return a JSON list of temperature observations for the previous year.
    for date, tobs in temp:
        temp_dict[date] = tobs

    return jsonify(temp_dict)


#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

# Dynamic Start 
@app.route('/api/v1.0/<start>')

def start_date(start):
    start_date = session.query(func.min(Measurements.tobs), func.max(Measurements.tobs), func.avg(Measurements.tobs)).filter(Measurements.date >= start).all()
    #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    temperature_stats = {
        'minimum temperature': start_date[0][0],
        'maximum temperature': start_date[0][1],
        'average temperature': start_date[0][2]
    }

    return jsonify(temperature_stats)

# Dynamic Start and End
@app.route('/api/v1.0/<start>/<end>')

def start_and_end(start, end):
    start_and_end_date = session.query(func.min(Measurements.tobs), func.max(Measurements.tobs), func.avg(Measurements.tobs)).filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    temperature_stats = {
        'minimum temperature': start_and_end_date[0][0],
        'maximum temperature': start_and_end_date[0][1],
        'average temperature': start_and_end_date[0][2]
    }

    return jsonify(temperature_stats)
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
if __name__ == "__main__":
    app.run(debug=True)
