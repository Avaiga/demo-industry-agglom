import functools
import pandas as pd
import pickle
from pathlib import Path
import pickle


_DATA_DIR = Path(__file__).parent

@functools.cache
def get_data_df():
    parquet_path = _DATA_DIR / "Proximity-Adjusted LQ.parquet"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    dtypes = pickle.load(open(_DATA_DIR / "dtypes.pkl", "rb"))
    df = pd.read_csv(_DATA_DIR / "Proximity-Adjusted LQ.csv", dtype=dtypes)
    df.to_parquet(parquet_path)
    return df


def get_metadata_df():
    metadata_path = _DATA_DIR / "Proximity-Adjusted LQ Metadata.csv"
    metadata_df = pd.read_csv(metadata_path, skiprows=4, usecols=range(3))
    return metadata_df
