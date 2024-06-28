import geopandas as gpd
from shapely.geometry import Polygon, Point
import numpy as np
import json


class GeographicalProcessing:
    def json_to_geodataframe(self, json_data):
        geometries = []

        for feature in json_data["features"]:
            poly = Polygon(feature["geometry"]["coordinates"][0])
            geometries.append(poly)

        gdf = gpd.GeoDataFrame(geometry=geometries, crs="EPSG:4326")
        return gdf

    def create_mask(self, czech_rep, grid_x, grid_y):
        mask = np.zeros_like(grid_x, dtype=bool)
        for i in range(grid_x.shape[0]):
            for j in range(grid_x.shape[1]):
                point = Point(grid_x[i, j], grid_y[i, j])
                mask[i, j] = czech_rep.contains(point).any()
        return mask

    def load_country_data(self, country_file_path):
        with open(country_file_path, "r", encoding="utf-8") as file:
            return json.load(file)
