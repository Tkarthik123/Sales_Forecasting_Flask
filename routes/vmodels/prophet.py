'''from prophet import Prophet
import pandas as pd
import os
from routes.vmodels.utils import save_forecast
def forecast_with_prophet(filepath, category, username,forecast_period,order_cost,holding_cost):
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
    future = model.make_future_dataframe(periods=forecast_period)
    forecast = model.predict(future)

    forecast_df = forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Forecast'})
    forecast_df = forecast_df[forecast_df['Date'] > df['ds'].max()]

    total_demand = forecast_df['Forecast'].sum()
    order_cost = order_cost
    holding_cost = holding_cost
    eoq = calculate_eoq(total_demand, order_cost, holding_cost)
    eoq_row = pd.DataFrame([{'Date': 'EOQ (units)', 'Forecast': eoq}])
    forecast_df = pd.concat([forecast_df, eoq_row], ignore_index=True)
    filename = f"Prophet_{category}_forecast.csv"
    save_forecast(forecast_df, username, category, "Prophet")

    return {
        "file": filename,
        "data": forecast_df.to_dict(orient='records'),
        "eoq": eoq
    }

def calculate_eoq(annual_demand, order_cost, holding_cost):
    return round((2 * annual_demand * order_cost / holding_cost) ** 0.5, 2)'''

from prophet import Prophet
import pandas as pd
import os
from routes.vmodels.utils import save_forecast

def forecast_with_prophet(filepath, category, username, forecast_period, order_cost, holding_cost):
    print("Using Prophet")

    # Read and prepare data
    df = pd.read_csv(filepath)
    category_col, value_col, date_col = df.columns[:3]
    df = df[df[category_col] == category]
    df[date_col] = df[date_col].str.replace('-', '/', regex=False)
    df[date_col] = pd.to_datetime(df[date_col], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=[date_col])
    df = df[[date_col, value_col]].groupby(date_col).sum().reset_index()
    df.rename(columns={date_col: 'ds', value_col: 'y'}, inplace=True)

    # Fit model
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=forecast_period)
    forecast = model.predict(future)

    # Prepare forecast output
    forecast_df = forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Forecast'})
    forecast_df = forecast_df[forecast_df['Date'] > df['ds'].max()]

    # EOQ Calculation (kept separate)
    total_demand = forecast_df['Forecast'].sum()
    eoq = calculate_eoq(total_demand, order_cost, holding_cost)
    num_orders = round(total_demand / eoq)

    # Save forecast only (NO EOQ row in file)
    filename = f"Prophet_{category}_forecast.csv"
    save_forecast(forecast_df, username, category, "Prophet")

    # Return clean result
    return {
        "file": filename,
        "data": forecast_df.to_dict(orient='records'),
        "eoq": {
            "category": category,
            "forecast_demand": total_demand,
            "order_cost": order_cost,
            "holding_cost": holding_cost,
            "optimal_order_quantity": eoq,
            "number_of_orders": num_orders
    }
    }

def calculate_eoq(annual_demand, order_cost, holding_cost):
    return round((2 * annual_demand * order_cost / holding_cost) ** 0.5, 2)

