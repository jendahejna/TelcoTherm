import numpy as np
from interpolation.interpolator import IdwKdtreeInterpolator
from scipy.interpolate import griddata
from pykrige.rk import RegressionKriging
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR

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


def spatial_interpolation(df, czech_rep, geo_proc, elevation_data, lon_elev, lat_elev, variogram_model='spherical',
                          nlags=40, regression_model_type='linear'):
    # Krok 1: Vytvoření gridu a masky
    czech_bounds = czech_rep.total_bounds
    grid_x, grid_y = np.mgrid[
                     czech_bounds[0]:czech_bounds[2]:500j,
                     czech_bounds[1]:czech_bounds[3]:500j
                     ]
    grid_points = np.c_[grid_x.ravel(), grid_y.ravel()]
    mask = geo_proc.create_mask(czech_rep, grid_x, grid_y)

    # Krok 2: Příprava vstupních dat
    valid_points = (~df['Longitude'].isna()) & (~df['Latitude'].isna()) & (~df['Predicted_Temperature'].isna())
    lon = df.loc[valid_points, 'Longitude'].values
    lat = df.loc[valid_points, 'Latitude'].values
    temp = df.loc[valid_points, 'Predicted_Temperature'].values

    points = np.c_[lon_elev.ravel(), lat_elev.ravel()]
    values = elevation_data.ravel()
    valid_elev = griddata(points, values, (lon, lat), method='linear')

    if np.isnan(valid_elev).any():
        valid_elev = np.nan_to_num(valid_elev, nan=np.nanmean(valid_elev))

    if not (len(lon) == len(lat) == len(temp) == len(valid_elev)):
        raise ValueError("Rozměry souřadnic, teploty a elevace nejsou stejné. Zkontrolujte vstupní data.")

    # Krok 3: Výběr regresního modelu
    if regression_model_type == 'linear':
        regression_model = LinearRegression()
    elif regression_model_type == 'random_forest':
        regression_model = RandomForestRegressor(n_estimators=100, random_state=42)
    elif regression_model_type == 'gradient_boosting':
        regression_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    elif regression_model_type == 'svr':
        regression_model = SVR(kernel='rbf', C=1.0, epsilon=0.1)
    else:
        raise ValueError(f"Neznámý typ regresního modelu: {regression_model_type}")

    # Krok 4: Nastavení Regression Kriging modelu
    X = valid_elev.reshape(-1, 1)
    rk = RegressionKriging(
        regression_model=regression_model,
        variogram_model=variogram_model,
        n_closest_points=nlags
    )

    # Trénování Regression Kriging modelu
    rk.fit(X, np.c_[lon, lat], temp)

    # Predikce na gridu
    grid_elev = griddata(points, values, (grid_x, grid_y), method='linear')

    if np.isnan(grid_elev).any():
        grid_elev = np.nan_to_num(grid_elev, nan=np.nanmean(valid_elev))

    grid_predicted_temp = rk.predict(grid_elev.reshape(-1, 1), np.c_[grid_x.ravel(), grid_y.ravel()])
    grid_predicted_temp = grid_predicted_temp.reshape(grid_x.shape)

    # Aplikace masky
    grid_predicted_temp = np.where(mask.reshape(grid_x.shape), grid_predicted_temp, np.nan)

    return grid_x, grid_y, grid_predicted_temp