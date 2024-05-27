import os

import pandas as pd
from flask import Blueprint, request, jsonify
from sqlalchemy import Table

from una_health.database import metadata, engine
from una_health.models import GlucoseTrack
from una_health.utils import clean_cols_with_nan

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return "Hello, Docker!"

#
@main.route('/api/v1/levels/', methods=['GET'])
def glucose_levels():
    # Get the params from the client side
    user_id = request.args.get('user_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Filter the query for fetching for the specified user_id
    query = GlucoseTrack.query.filter(GlucoseTrack.user_id == user_id)

    # start_time and end_time filter is optional
    if start_time:
        query = query.filter(GlucoseTrack.device_timestamp >= start_time)
    if end_time:
        query = query.filter(GlucoseTrack.device_timestamp <= end_time)

    # show the list in descending order of the device timestamp i.e the list shows the current data first
    query = query.order_by(GlucoseTrack.device_timestamp.desc())
    # only few entries are returned based on the page number and per_page data number
    glucose_info = query.paginate(page=page, per_page=per_page)
    result = {
        "items": [item.to_dict() for item in glucose_info.items]
    }

    return jsonify(result)


@main.route('/api/v1/levels/<string:id>/', methods=['GET'])
def glucose_levels_by_id(id):
    # assuming id to be user_id
    glucose_info = GlucoseTrack.query.filter(GlucoseTrack.user_id == id).all()
    result = {
        "items": [item.to_dict() for item in glucose_info]
    }
    return jsonify(result)


@main.route('/api/v1/populate_db/', methods=['POST'])
def populate_db():
    current_dir = os.getcwd()
    is_docker = os.getenv('DOCKER') == 'true'
    # if is_docker:
    #     current_dir = '/usr/src/app/una_health/data_files/'
    # else:
    #     current_dir = current_dir + '\\una_health\\data_files\\'

    current_dir = os.path.join(current_dir, 'una_health', 'data_files/')

    df = pd.DataFrame()
    # Get the data from the excel files and preprocessing it
    for file in os.listdir(current_dir):
        if file.endswith(r'.csv'):
            temp_df = pd.read_csv(current_dir + file, skiprows=2)
            temp_df = clean_cols_with_nan(temp_df)
            temp_df['user_id'] = file.split('.csv')[0]

        df = pd.concat([df, temp_df], axis=0)

    # column name mapping for german to english column names
    column_mapping = {'Gerat': 'device', 'Seriennummer': 'serial_number',
                      'Geratezeitstempel': 'device_timestamp',
                      'Aufzeichnungstyp': 'recording_type',
                      'Glukosewert-Verlauf mg/dL': 'glucose_level'}
    df.rename(columns=column_mapping, inplace=True)
    df = df[['user_id', 'device_timestamp', 'device', 'serial_number',
             'recording_type', 'glucose_level']]

    df = df[~df['glucose_level'].isna()]

    glucose_tracks_table = Table('glucose_track', metadata, autoload_with=engine)

    try:
        # Bulk insert
        with engine.connect() as conn:
            conn.execute(glucose_tracks_table.insert(), df.to_dict(orient='records'))
            conn.commit()
        return jsonify({"message": "Database populated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


@main.route('/api/v1/export_to_excel/', methods=['POST'])
def export_to_excel():
    glucose_info = GlucoseTrack.query.all()
    glucose_info_dict = [item.to_dict() for item in glucose_info]
    df = pd.DataFrame(glucose_info_dict)
    df.to_excel('glucose_level_data.xlsx')
    return jsonify({"message": "Exported to Excel successfully"})