import os
def save_forecast(df, username, category, model):
    folder = os.path.join("forecasted_uploads", username)
    os.makedirs(folder, exist_ok=True)

    filename = f"{model}_{category}_forecast.csv"
    path = os.path.join(folder, filename)

    df.to_csv(path, index=False)