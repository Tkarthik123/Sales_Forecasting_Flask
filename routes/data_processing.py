import os
import pandas as pd
from app import app
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER ="processed_uploads"
def get_attributes(filename, username):
    """Extract column names from uploaded file."""
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    processed_user_folder = os.path.join(PROCESSED_FOLDER, username)
    file_path = os.path.join(user_folder, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found!"}

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return {"error": "Unsupported file format!"}

        return {"attributes": df.columns.tolist()}

    except Exception as e:
        return {"error": str(e)}
print("worked")
def process_data(filename, username, selected_columns):
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    processed_user_folder = os.path.join(PROCESSED_FOLDER, username)
    file_path = os.path.join(user_folder, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found!"}

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return {"error": "Unsupported file format!"}

        # Select only the required columns
        df_selected = df[selected_columns]
        df_selected.dropna(how='any', axis=0, inplace=True)

        # Perform any preprocessing steps (e.g., handling missing values)
        processed_filename = f"processed_{filename}"
        os.makedirs(processed_user_folder, exist_ok=True)
        processed_path = os.path.join(processed_user_folder, processed_filename)
        df_selected.to_csv(processed_path, index=False)

        print(f"\n==== Processed Data Saved at: {processed_path} ====")
        print(df_selected.head())  # Display first 5 rows
        preview_data = df_selected.head(5).to_dict(orient='records')
        category_column = selected_columns[0]
        unique_categories = df_selected[category_column].dropna().unique().tolist()
        return {
            "processed_file": processed_filename,
            "preview": preview_data,
            "categories": unique_categories,
            "message": "Data processing successful!"
        }
    except Exception as e:
        print("❌ Error processing data:", e)
        return {"error": str(e)}