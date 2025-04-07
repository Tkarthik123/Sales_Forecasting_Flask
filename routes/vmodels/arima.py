import pandas as pd
import os
from statsmodels.tsa.arima.model import ARIMA
from routes.vmodels.utils import save_forecast
def forecast_with_arima(filepath, category, username):
    print("Using ARIMA")
    df = pd.read_csv(filepath)
    category_col, value_col, date_col = df.columns[:3]

    df = df[df[category_col] == category]
    df[date_col] = df[date_col].str.replace('-', '/', regex=False)
    df[date_col] = pd.to_datetime(df[date_col], format='%m/%d/%Y')
    df = df[[date_col, value_col]].groupby(date_col).sum().asfreq('D').fillna(0)

    model = ARIMA(df[value_col], order=(1, 1, 1))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=30)

    forecast_df = pd.DataFrame({
        'Date': pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=30),
        'Forecast': forecast.values
    })

    filename = f"ARIMA_{category}_forecast.csv"
    save_forecast(forecast_df, username, category, "ARIMA")

    return {
        "file": filename,
        "data": forecast_df.to_dict(orient='records')
    }