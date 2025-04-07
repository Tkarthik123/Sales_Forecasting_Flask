# views.py or visualization.py
from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import os

visualization = Blueprint('visualization', __name__)

@visualization.route('/visualize', methods=['GET'])
def visualize():
    file_name = request.args.get('file')  # e.g., Prophet_Furniture_forecast.csv
    file_path = os.path.join('forecasted_uploads', file_name)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    df = pd.read_csv(file_path)
    forecast_data = {
        'dates': df['ds'].tolist(),
        'forecast': df['yhat'].tolist(),
        'lower': df.get('yhat_lower', []).tolist(),
        'upper': df.get('yhat_upper', []).tolist()
    }
    return jsonify(forecast_data)