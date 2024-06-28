import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json
import numpy as np
from sqlalchemy.exc import IntegrityError

backend_logger = logging.getLogger('backend_logger')
class DatabaseOperations:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_metadata(self, df):
        sites = []
        azimuths = []
        latitudes = []
        longitudes = []
        links = []
        devices = 0
        with self.Session() as session:
            for index, row in df.iterrows():
                ip_address = row["IP"].strip()

                try:
                    result = session.execute(
                        text(
                            "SELECT ID, site_A, site_B, azimuth_A, azimuth_B, IP_address_A, IP_address_B FROM cml_metadata.links WHERE IP_address_A=:ip OR IP_address_B=:ip"
                        ),
                        {"ip": ip_address},
                    ).fetchone()

                    if result:
                        devices += 1
                        (
                            link_id,
                            site_a,
                            site_b,
                            azimuth_a,
                            azimuth_b,
                            ip_address_a,
                            ip_address_b,
                        ) = result

                        if ip_address == ip_address_a:
                            azimuth = azimuth_a
                            site_id = site_a

                        elif ip_address == ip_address_b:
                            azimuth = azimuth_b
                            site_id = site_b

                        else:
                            azimuth, site_id = None, None
                            backend_logger.warning(
                                f"Azimuth and Site_ID cannot be assigned for IP: {ip_address}"
                            )

                        site_result = session.execute(
                            text(
                                "SELECT X_coordinate, Y_coordinate FROM cml_metadata.sites WHERE id=:site_id"
                            ),
                            {"site_id": site_id},
                        ).fetchone()

                        if site_result:
                            longitude, latitude = site_result

                        else:
                            latitude, longitude = None, None
                            backend_logger.warning(
                                f"No coordinates found for site ID: {site_id}"
                            )

                    else:
                        #backend_logger.warning(f"No link result found for IP: {ip_address}")
                        pass
                    azimuths.append(azimuth)
                    sites.append(site_id)
                    links.append(link_id)
                    latitudes.append(latitude)
                    longitudes.append(longitude)

                except Exception as e:
                    backend_logger.error(f"Error in get_metadata for IP {ip_address}: {e}")
                    continue

        backend_logger.info(f"Completed get_metadata method for {devices} devices.")
        return latitudes, longitudes, azimuths, links

    def realtime_writer(self, image_name, unique_links_list, current_datetime, grid_z):
        unique_links_list = [int(link) for link in unique_links_list]
        TEMP_MIN = round(np.nanmin(grid_z.ravel()))
        TEMP_MAX = round(np.nanmax(grid_z.ravel()))
    
        with self.Session() as session:
            try:
                session.execute(
                    text(
                        """
                        INSERT INTO telcorain_output.realtime_temperature_grids 
                        (time, links, image_name, TEMP_MIN, TEMP_MAX) 
                        VALUES (:time, :links, :image_name, :TEMP_MIN, :TEMP_MAX)
                        """
                    ),
                    {
                        "time": current_datetime,
                        "links": json.dumps(unique_links_list),
                        "image_name": image_name,
                        "TEMP_MIN": TEMP_MIN,
                        "TEMP_MAX": TEMP_MAX,
                    },
                )
                session.commit()
                backend_logger.info(
                    f"Interpolation data from {current_datetime} successfully recorded."
                )
            except IntegrityError as e:
                session.rollback()
                backend_logger.warning(f"Duplicate entry error: {e}")
    
            except Exception as e:
                session.rollback()
                backend_logger.error(f"Error in realtime_writer: {e}")
    
    
    def save_parameters(self, current_datetime, grid_x, grid_y):
        with self.Session() as session:
            try:
                X_MIN = round(np.nanmin(grid_x.ravel()), 4)
                X_MAX = round(np.nanmax(grid_x.ravel()), 4)
                Y_MIN = round(np.nanmin(grid_y.ravel()), 4)
                Y_MAX = round(np.nanmax(grid_y.ravel()), 4)
                retention = 43200  # V sekundách
                timestep = 1800  # V sekundách
                X_COUNT = Y_COUNT = 500
                images_URL = "http://192.168.64.100/images"
    
                session.execute(
                    text(
                        """
                        INSERT INTO telcorain_output.realtime_temperature_parameters
                        (started, retention, timestep, X_MIN, X_MAX, Y_MIN, Y_MAX, X_COUNT, Y_COUNT, images_URL)
                        VALUES (:started, :retention, :timestep, :X_MIN, :X_MAX, :Y_MIN, :Y_MAX, :X_COUNT, :Y_COUNT, :images_URL)
                        """
                    ),
                    {
                        "started": current_datetime,
                        "retention": retention,
                        "timestep": timestep,
                        "X_MIN": X_MIN,
                        "X_MAX": X_MAX,
                        "Y_MIN": Y_MIN,
                        "Y_MAX": Y_MAX,
                        "X_COUNT": X_COUNT,
                        "Y_COUNT": Y_COUNT,
                        "images_URL": images_URL,
                    },
                )
                session.commit()
                backend_logger.info(
                    f"Parameters data for {current_datetime} successfully recorded."
                )
            except Exception as e:
                session.rollback()
                backend_logger.error(f"Error in save_parameters: {e}")
