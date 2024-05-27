import os

import pandas as pd
from flask import Blueprint, request, jsonify
from sqlalchemy import Table

from una_health.database import metadata, engine
from una_health.models import GlucoseTrack
from una_health.utils import clean_cols_with_nan

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/api/v1/levels/', methods=['GET'])
def glucose_levels():
    user_id = request.args.get('user_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = GlucoseTrack.query.filter(GlucoseTrack.user_id == user_id)

    if start_time:
        query = query.filter(GlucoseTrack.device_timestamp >= start_time)
    if end_time:
        query = query.filter(GlucoseTrack.device_timestamp <= end_time)

    query = query.order_by(GlucoseTrack.device_timestamp.desc())
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
    current_dir = current_dir + '\\una_health\\data_files\\'
    df = pd.DataFrame()
    for file in os.listdir(current_dir):
        if file.endswith(r'.csv'):
            temp_df = pd.read_csv(current_dir + file, skiprows=2)
            temp_df = clean_cols_with_nan(temp_df)
            temp_df['user_id'] = file.split('.csv')[0]

        df = pd.concat([df, temp_df], axis=0)

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