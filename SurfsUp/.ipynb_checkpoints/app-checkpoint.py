# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify


############################################
# Database Setup
############################################
# Reflect an existing database into a new model
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Save references to each table
measurement_table = Measurement
station_table = Station

# Create our session (link) from Python to the DB
session = Session(engine)

############################################
# Flask Setup
############################################
app = Flask(__name__)

############################################
# Flask Routes
############################################
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON list of precipitation data."""
    # Calculate the date one year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert to dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    results = session.query(Station.station).all()
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    temperature_data = [{date: temp} for date, temp in results]

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return min, avg, and max temperatures from a start date."""
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    temps = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return min, avg, and max temperatures between start and end dates."""
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temps = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
