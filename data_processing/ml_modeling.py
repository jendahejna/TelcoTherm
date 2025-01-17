import joblib
from tensorflow.keras.models import load_model
import joblib


scaler = joblib.load("neural/scaler.joblib")
# Further development: Training and adding more ML models
def predict_temperature(df):
    X = df.drop(["Time", "Latitude", "Longitude", "IP", "Link_ID", "Hour"], axis=1)
    model = joblib.load("Linear_model_final1.joblib")
    predicted_temperatures = model.predict(X)
    df["Predicted_Temperature"] = predicted_temperatures
    df = (
        df.groupby(["Hour", "IP", "Latitude", "Longitude"])["Predicted_Temperature"]
        .mean()
        .reset_index()
    )
    return df

def temperature_predict(df):
    col_order = ['Temperature_MW', 'sun', 'Hour', 'Day', 'Signal', 'Azimuth']
    X = df[col_order]
    X_scaled = scaler.transform(X)
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))
    model = load_model("neural/best_lstm_model.h5", compile=False)
    predicted_temperatures = model.predict(X_reshaped).flatten()
    df["Predicted_Temperature"] = predicted_temperatures
    df = (
        df.groupby(["Hour", "IP", "Latitude", "Longitude"])["Predicted_Temperature"]
        .mean()
        .reset_index()
    )
    return df

