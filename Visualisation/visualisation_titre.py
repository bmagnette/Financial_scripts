# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 12:19:07 2017

@author: Baptiste
"""

from pandas_datareader import data as pdr
import pandas as pd
import matplotlib.pyplot as plt
import fix_yahoo_finance as yf
yf.pdr_override()


def get_input():
    start_date = input("Start Date : ")
    end_date = input("End Date : ")
    title = input("Entreprise :")
    return start_date, end_date, title


def get_data(start_date, end_date, title):
    dates = pd.date_range(start_date, end_date)
    df = pd.DataFrame(index=dates)
    df_temp = pdr.get_data_yahoo(title, start=start_date, end=end_date)
    df_temp = df_temp.rename(columns={'Adj Close' : title})
    df_temp = pd.to_numeric(df_temp[title])
    df = df.join(df_temp)
    df = df.dropna()
    print(df.head(5))
    return df


def get_competitor(title):
    return ''


def plot_data(df):
    df = normalize(df)
    ax = df.plot(title="Stock Prices", fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

    
def normalize(df):
    return df/df.iloc[0, :]


start_date, end_date, title = get_input()
list_competitor = get_competitor(title)
plot_data(get_data(start_date, end_date, title))
