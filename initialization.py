import logging
from sqlalchemy import create_engine
from database_operations.database_operations import DatabaseOperations
from spatial_processing.geographical_processing import GeographicalProcessing
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from time import sleep

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

CZECH_DATA_PATH = "country_data/czech_republic.json"
TIF_PATH = "country_data/elevation_data.tif"


def wait_for_next_hour():
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    sleep((next_hour - now).seconds)

def initialize_app(config, data_path, tif_path):
    engine = create_engine(
        f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}"
    )
    db_ops = DatabaseOperations(engine)
    geo_proc = GeographicalProcessing()
    state = geo_proc.load_country_data(data_path)
    czech_rep = geo_proc.json_to_geodataframe(state)
    elevation_data, lon_elev, lat_elev = geo_proc.load_elevation_data(tif_path)
    return db_ops, geo_proc, czech_rep, elevation_data, lon_elev, lat_elev
