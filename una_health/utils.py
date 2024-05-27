

def clean_cols_with_nan(df):
    for col in df.columns:
        if df[col].isna().all():
            df.drop([col], axis=1, inplace=True)

    return df