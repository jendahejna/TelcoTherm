import geopandas as gpd
from shapely.geometry import Polygon, Point
import numpy as np
import json
import rasterio
from pyproj import Transformer

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

    def load_elevation_data(self, tif_path):
        with rasterio.open(tif_path) as src:
            transformer = Transformer.from_crs("EPSG:3045", "EPSG:4326", always_xy=True)
            transform_matrix = src.transform
            width = src.width
            height = src.height

            x_pixels, y_pixels = np.meshgrid(np.arange(width), np.arange(height))
            x_coords, y_coords = rasterio.transform.xy(transform_matrix, y_pixels, x_pixels)
            lon, lat = transformer.transform(x_coords, y_coords)

            elevation_data = src.read(1)
            nodata_value = -3.4028234663852886e+38
            elevation_data = np.where(elevation_data == nodata_value, np.nan, elevation_data)

        return elevation_data, lon, lat
