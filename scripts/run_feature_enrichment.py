import os

import pandas as pd
from src.indicators.feature_enricher import apply_indicators
from src.utils.file_util import save_df_to_csv, HISTORICAL_DATA_DIR, FEATURE_DATA_DIR


def perform_file_enrichment(filename):
    file_path = os.path.join(HISTORICAL_DATA_DIR, filename)
    df = pd.read_csv(file_path)
    print(f"Processing historical data file: {file_path}")

    # Feature enrichment
    df = apply_indicators(df)

    # Dataframe cleanup
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Save feature enriched file
    name, ext = os.path.splitext(filename)
    feature_filename = f"{name}_feat{ext}"
    enriched_output_path = os.path.join(FEATURE_DATA_DIR, feature_filename)
    save_df_to_csv(df, enriched_output_path)

    print(f"Saved enriched features to: {enriched_output_path}")


def single_file_enrichment():
    filename = "HDFCBANK_minute.csv"
    perform_file_enrichment(filename)


def multi_files_enrichment():
    for filename in os.listdir(HISTORICAL_DATA_DIR):
        perform_file_enrichment(filename)


if __name__ == "__main__":
    single_file_enrichment()
    # multi_files_enrichment()
