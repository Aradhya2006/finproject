import pandas as pd

def calculate_daily_returns(df):
    df = df.copy()
    df["DAILY RETURN"] = ( (df["CLOSE"] / df["CLOSE"].shift(1)) -1  )

    return df