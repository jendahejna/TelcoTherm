import numpy as np
from scipy.interpolate import griddata
from interpolation.interpolator import IdwKdtreeInterpolator
from config import GRID_RESOLUTION_X, GRID_RESOLUTION_Y


def interpolate_temperature_new(df, czech_rep, geo_proc):
    czech_bounds = czech_rep.bounds
    grid_x, grid_y = np.mgrid[
        czech_bounds.minx.min() : czech_bounds.maxx.max() : 1280j,
        czech_bounds.miny.min() : czech_bounds.maxy.max() : 720j,
    ]
    mask = geo_proc.create_mask(czech_rep, grid_x, grid_y)

    # Příprava dat pro interpolaci
    points = np.column_stack((df["Longitude"].values, df["Latitude"].values))
    values = df["Predicted_Temperature"].values
    grid_points = np.column_stack((grid_x[mask], grid_y[mask]))

    # Provedení interpolace
    grid_z_masked = griddata(points, values, grid_points, method="nearest")

    # Vytvoření výsledného rastru s využitím masky
    grid_z = np.full(grid_x.shape, np.nan)
    grid_z[mask] = grid_z_masked

    return grid_x, grid_y, grid_z


def interpolate_temperature_old(df, czech_rep, geo_proc):
    czech_bounds = czech_rep.bounds
    grid_x, grid_y = np.mgrid[
        czech_bounds.minx.min():czech_bounds.maxx.max():1280j,
        czech_bounds.miny.min():czech_bounds.maxy.max():720j,
    ]
    mask = geo_proc.create_mask(czech_rep, grid_x, grid_y)

    idw_interpolator = IdwKdtreeInterpolator(
        nnear=10, p=1, exclude_nan=True, max_distance=1
    )

    grid_x_masked = grid_x[mask]
    grid_y_masked = grid_y[mask]

    grid_z_masked = idw_interpolator(
        df["Longitude"].values,
        df["Latitude"].values,
        df["Predicted_Temperature"].values,
        xgrid=grid_x_masked,
        ygrid=grid_y_masked,
    )

    grid_z = np.full(grid_x.shape, np.nan)
    grid_z[mask] = grid_z_masked

    return grid_x, grid_y, grid_z

def interpolate_temperature(df, czech_rep, geo_proc):
    czech_bounds = czech_rep.bounds
    grid_x, grid_y = np.mgrid[
        czech_bounds.minx.min():czech_bounds.maxx.max():1280j,
        czech_bounds.miny.min():czech_bounds.maxy.max():720j,
    ]
    mask = geo_proc.create_mask(czech_rep, grid_x, grid_y)
    idw_interpolator = IdwKdtreeInterpolator(
        nnear=10, p=1, exclude_nan=True, max_distance=1
    )
    grid_x_masked = grid_x[mask]
    grid_y_masked = grid_y[mask]
    grid_z_masked = idw_interpolator(
        df["Longitude"].values,
        df["Latitude"].values,
        df["Predicted_Temperature"].values,
        xgrid=grid_x_masked,
        ygrid=grid_y_masked,
    )
    grid_z = np.full(grid_x.shape, np.nan)
    grid_z[mask] = grid_z_masked

    return grid_x, grid_y, grid_z