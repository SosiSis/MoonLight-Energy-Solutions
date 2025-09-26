# src/data_load.py
import pandas as pd
from typing import Dict

EXPECTED_COLUMNS = [
    "Timestamp","GHI","DNI","DHI","ModA","ModB","Tamb","RH","WS","WSgust",
    "WSstdev","WD","WDstdev","BP","Cleaning","Precipitation","TModA","TModB","Comments"
]

def load_csv(path: str, parse_dates=True) -> pd.DataFrame:
    df = pd.read_csv(path)
    if parse_dates and "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M", errors='coerce')
        df = df.sort_values("Timestamp").reset_index(drop=True)
    return df

def load_country_files(file_map: Dict[str,str]) -> Dict[str,pd.DataFrame]:
    """
    file_map: {"Benin": "data/raw/benin.csv", ...}
    """
    return {country: load_csv(path) for country, path in file_map.items()}
