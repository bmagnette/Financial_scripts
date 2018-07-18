# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 12:19:07 2017

@author: Baptiste
"""
from typing import Tuple

import fix_yahoo_finance as yf
import matplotlib.pyplot as plt
import pandas as pd
from pandas_datareader import data as pdr


def get_input() -> Tuple[str, str, str]:
    """
    Get data from console input
    """

    start_date_input = input("Start Date (Y-m-d): ")
    end_date_input = input("End Date (Y-m-d): ")
    yahoo_tickers_input = input("Enterprise :")

    return start_date_input, end_date_input, yahoo_tickers_input


def get_data(start_bands: str, end_bands: str, tickers_list: str) -> pd.DataFrame:
    """
    Concatenate OCHL data to get tickers dataframe.
    """

    tickers_list = tickers_list.split(',')
    dates = pd.date_range(start_bands, end_bands)
    main_df = pd.DataFrame(index=dates)

    for company in tickers_list:
        # For each company request yahoo and do treatment on data.
        df_temp = pdr.get_data_yahoo(company, start=start_bands, end=end_bands)

        # Treatment
        df_temp = df_temp.rename(columns={'Adj Close': company})
        df_temp = pd.to_numeric(df_temp[company])
        main_df = main_df.join(df_temp)
        main_df = main_df.dropna()

    return main_df


def plot_data(data: pd.DataFrame)-> None:
    """
    Plot data using matplotlib
    """

    data = normalizer(data)
    ax = data.plot(title="Stock Prices", fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()


def normalizer(raw_data: pd.DataFrame) -> pd.DataFrame:
    """ Normalize data """
    return raw_data / raw_data.iloc[0, :]


if __name__ == '__main__':
    yf.pdr_override()

    start_date, end_date, tickers = get_input()
    df = get_data(start_date, end_date, tickers)

    plot_data(df)
