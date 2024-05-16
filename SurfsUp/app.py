# Import the dependencies.
import os
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, func, text
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, declarative_base
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine,reflect=True)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def ltm_precipitation_data():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT max(date) FROM Measurement'))
        for record in result:
            last_date=record[0]
    last_date_2 = datetime.strptime(last_date, '%Y-%m-%d').date()

    previous_date=last_date_2-timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_date).\
    filter(Measurement.date <= last_date_2).all()


    if precipitation_data != []:
        result_dicts = [{column.name: getattr(row, column.name) for column in (Measurement.date,Measurement.prcp)} for row in precipitation_data]
        return jsonify(result_dicts)

    return jsonify({"error": f"No precipitation data available."}), 404

@app.route("/api/v1.0/stations")
def stations_list():
    result_stations=session.query(Station.station,Station.name).all()
    
    if result_stations:
        station_result_dicts = [{"station": row[0],"name":row[1]} for row in result_stations]
        return jsonify(station_result_dicts)
    else:
        return jsonify({"error": "No station data available."}), 404

@app.route("/api/v1.0/tobs")
def ltm_temperature_data():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT max(date) FROM Measurement'))
        for record in result:
            last_date=record[0]
    last_date_2 = datetime.strptime(last_date, '%Y-%m-%d').date()

    previous_date=last_date_2-timedelta(days=365)

    station_data=session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    temp_data = session.query(Measurement.tobs).filter(Measurement.date >= previous_date).\
    filter(Measurement.date <= last_date_2).\
    filter(Measurement.station==station_data[0][0]).all()

    if temp_data != []:
        temp_result_dicts = [{"tobs": row[0]} for row in temp_data]
        return jsonify(temp_result_dicts)
    return jsonify({"error": f"No temperature data available."}), 404

@app.route("/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>")
def temp_info(start,end=None):
    if end != None:
        result_temp_info=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    else:
        result_temp_info=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
     
    
    if result_temp_info != []:
        temp_info_result_dicts = [{"TMIN": row[0],"TAVG": row[1],"TMAX":row[2]} for row in result_temp_info]
        return jsonify(temp_info_result_dicts)
    return jsonify({"error": f"No temperature data available."}), 404


if __name__ == '__main__':
    app.run()
    

