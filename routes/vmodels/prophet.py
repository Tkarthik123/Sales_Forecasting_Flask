from prophet import Prophet
import pandas as pd
import os
from routes.vmodels.utils import save_forecast
def forecast_with_prophet(filepath, category, username):
    print("Using Prophet")
    df = pd.read_csv(filepath)
    category_col, value_col, date_col = df.columns[:3]

    df = df[df[category_col] == category]
    df[date_col] = df[date_col].str.replace('-', '/', regex=False)
    df[date_col] = pd.to_datetime(df[date_col], format='%m/%d/%Y')
    
    df = df[[date_col, value_col]].groupby(date_col).sum().reset_index()
    df.rename(columns={date_col: 'ds', value_col: 'y'}, inplace=True)

    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    forecast_df = forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Forecast'})
    forecast_df = forecast_df[forecast_df['Date'] > df['ds'].max()]

    filename = f"Prophet_{category}_forecast.csv"
    save_forecast(forecast_df, username, category, "Prophet")

    return {
        "file": filename,
        "data": forecast_df.to_dict(orient='records')
    }