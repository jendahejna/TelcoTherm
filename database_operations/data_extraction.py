import logging
from influxdb_client import InfluxDBClient
import pandas as pd
from astral.sun import sun
from astral import LocationInfo
import pytz
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Konstanty pro výpočet denního světla
LAT = 49.8175
LNG = 15.4730
PRAGUE_TZ = pytz.timezone("Europe/Prague")
load_dotenv()
token = os.getenv("INFLUX_TOKEN")
url = os.getenv("INFLUX_URL_PUBLIC")
org = os.getenv("ORG")
bucket = os.getenv("BUCKET")
backend_logger = logging.getLogger('backend_logger')


# Funkce pro zjištění denního světla
def is_daylight(time):
    location = LocationInfo(latitude=LAT, longitude=LNG)
    s = sun(location.observer, date=time.date())
    sunrise = s["sunrise"].astimezone(PRAGUE_TZ)
    sunset = s["sunset"].astimezone(PRAGUE_TZ)
    return 1 if sunrise <= time <= sunset else 0


# Funkce pro získání dat
def get_data(retry_count=3):
    for attempt in range(retry_count):
        try:
            with InfluxDBClient(url=url, token=token) as client:
                now_utc = datetime.utcnow()
                rounded_down_hour_utc = now_utc - timedelta(minutes=now_utc.minute, seconds=now_utc.second)



                query = f"""
                from(bucket: "{bucket}")
                  |> range(start: - 1h)
                  |> filter(fn: (r) => r["_measurement"] == "1s10")
                  |> filter(fn: (r) => r["_field"] == "Teplota" or r["_field"] == "PrijimanaUroven")
                  |> filter(fn: (r) => r["agent_host"] != "10.5.66.206")
                  |> filter(fn: (r) => r["agent_host"] != "10.200.110.5")
                  |> filter(fn: (r) => r["agent_host"] != "10.200.0.5")
                  |> filter(fn: (r) => r["agent_host"] != "10.1.13.207")
                  |> aggregateWindow(every: 5m, fn: mean)
                  |> group(columns: ["_measurement", "_field", "agent_host"])
                """

                result = client.query_api().query(org=org, query=query)

                # Přepracované zpracování dat
                data = [
                    {
                        "Time": record.get_time(),
                        "Measurement": record.values["_field"],
                        "Value": record.get_value(),
                        "IP": record.values["agent_host"],
                    }
                    for table in result
                    for record in table.records
                ]

                df = pd.DataFrame(data)
                df_pivot = df.pivot_table(
                    index=["Time", "IP"], columns="Measurement", values="Value"
                ).reset_index()
                df_pivot["Time"] = pd.to_datetime(df_pivot["Time"])
                df_pivot["Unix"] = df_pivot["Time"].astype("int64") // 10**9
                df_pivot["sun"] = df_pivot["Time"].apply(is_daylight)
                new_column_order = ["Time", "Unix", "Teplota", "PrijimanaUroven", "IP", "sun"]
                df_final = df_pivot[new_column_order].rename(
                    columns={"Teplota": "Temperature_MW", "PrijimanaUroven": "Signal"}
                )
                logging.info(f"Data úspěšně získána: {len(df_final)} záznamů")
                return df_final
        except Exception as e:
            backend_logger.warning(f"Nepodařilo se získat data: {e}")
            df_final = pd.DataFrame()
    return df_final

