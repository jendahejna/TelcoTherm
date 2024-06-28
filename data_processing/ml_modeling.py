import joblib


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
