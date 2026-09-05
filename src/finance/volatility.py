"""

sd = (   1                             )^1/2
       -------- sum(r_i - r_avg)^2
        n-1

        


annual sd  = daily sd * (252)^1/2
252 as there are 252 days for trading
"""

import pandas as pd
import numpy as np

def calculate_daily_volatility(df):
    returns = df["DAILY RETURN"].dropna()

    return np.std(returns , ddof = 1)


def calculate_annualized_volatility(df):
    daily_volatility = calculate_daily_volatility(df)

    return daily_volatility * np.sqrt(252)
