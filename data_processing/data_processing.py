import logging
from data_processing.ml_modeling import predict_temperature
from interpolation.interpolation import interpolate_temperature
from database_operations.data_extraction import get_data, is_daylight
from spatial_processing.visualization import get_heatmap
import pandas as pd
import datetime
import gc
import traceback

backend_logger = logging.getLogger("backend_logger")
first_run = True

def collect_data_summary(df):
    unique_links = df["Link_ID"].unique()
    unique_links_list = list(unique_links)

    image_time = df["Hour"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
    image_hour = df["Hour"].iloc[0].strftime("%Y-%m-%d_%H%M")
    image_name = f"{image_hour}.png"

    return unique_links_list, image_name, image_time


def prepare_data(df, latitudes, longitudes, azimuths, links):
    df["Azimuth"] = azimuths
    df["Latitude"] = latitudes
    df["Longitude"] = longitudes
    df["Link_ID"] = links

    df = df.dropna()

    df["Time"] = pd.to_datetime(df["Time"], utc=True)
    df["Time"] = df["Time"].dt.tz_convert("Europe/Prague")
    df["Hour"] = df["Time"].dt.round("H")

    return df


def process_data_round(db_ops, geo_proc, czech_rep):
    global first_run
    start_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    backend_logger.info(f"Calculation started on {start_datetime}")

    try:
        df = get_data()
        latitudes, longitudes, azimuths, links = db_ops.get_metadata(df)
        df = prepare_data(df, latitudes, longitudes, azimuths, links)
        unique_links_list, image_name, image_time = collect_data_summary(df)
        df = predict_temperature(df)
        grid_x, grid_y, grid_z = interpolate_temperature(df, czech_rep, geo_proc)
        db_ops.realtime_writer(image_name, unique_links_list, image_time, grid_z)
        db_ops.save_parameters(start_datetime, grid_x, grid_y)

        get_heatmap(grid_x, grid_y, grid_z, czech_rep, f"saved_grids/{image_name}")
    except Exception as e:
        backend_logger.error(f"Error during data processing round: {e}\n{traceback.format_exc()}")

    finally:
        if "df" in locals():
            del df
        gc.collect()
    end_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    backend_logger.info(
        f"Calculation ended on {end_datetime}. Waiting for another round.."
    )
