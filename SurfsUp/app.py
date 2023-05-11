# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# View all of the classes that automap found
Base.classes.keys()
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


# 2. /api/v1.0/precipitation

@app.route("/api/v1.0/precipitation")

def precipitation():

    # Query the results
    date_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_results = session.query(measurement.date, measurement.prcp).\
                    filter(measurement.date >= date_year_ago).all()
    

    # Create a dictionary from the row data and append to a list
    prcp_data = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)


# 3. /api/v1.0/stations

@app.route("/api/v1.0/stations")

def stations():

    # Query the results
    sta_results = session.query(station.station).all()

    # Convert the query results to a list
    sta_list = list(np.ravel(sta_results))

    # Return the list as JSON
    return jsonify(sta_list)


# 4. /api/v1.0/tobs
@app.route("/api/v1.0/tobs")

def tobs():

    date_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    active_s = session.query(measurement.station, func.count(measurement.station)).\
                group_by(measurement.station).\
                order_by(func.count(measurement.station).desc()).all()
    

    tob_results = session.query(measurement.tobs).\
                    filter(measurement.station == active_s[0][0]).\
                    filter(measurement.date >= date_year_ago).all()
    
    temps = list(np.ravel(tob_results))
    return jsonify(temps)


# 5.1 start route
@app.route("/api/v1.0/temp/<start>")

def start(start):

    sta_results =session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
                filter(measurement.station >= start).all()

    sta_tobs = list(np.ravel(sta_results))
    return jsonify(sta_tobs)


# 5.2 start/end route
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start, end):
    
    sta_results_2 =session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
                filter(measurement.station >= start).\
                filter(measurement.date <= end).all()

    sta_tobs_2 = list(np.ravel(sta_results_2))
    return jsonify(sta_tobs_2)



if __name__ == '__main__':
    app.run(debug=True)