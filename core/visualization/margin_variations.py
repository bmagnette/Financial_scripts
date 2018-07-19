import matplotlib.pyplot as plt
import pandas as pd
import requests

from core.screener.screener import get_financial, cleaner

ticker = "CAPLI.PA"


def turnover_ratio(df: pd.DataFrame()) -> pd.DataFrame():
    ratio_df = pd.DataFrame()

    ratio_df['RESULT/CA'] = df.loc['Bénéfice net', :].astype(
        float) / df.loc['Chiffre d’affaires total', :].astype(float)

    ratio_df['CAF/CA'] = df.loc['Flux total de trésorerie des activités d’exploitation', :].astype(
        float) / df.loc['Chiffre d’affaires total', :].astype(float)

    ratio_df['EBIT/CA'] = df.loc['Bénéfices avant intérêts et taxes', :].astype(float) / \
                                     df.loc['Chiffre d’affaires total', :].astype(float)
    return ratio_df


if __name__ == '__main__':

    main_df = get_financial(requests, ticker)

    # Remove duplicated
    main_df = main_df[~main_df.index.duplicated()]
    main_df.iloc[1:, :] = main_df.iloc[1:, :].applymap(cleaner)

    result_df = turnover_ratio(main_df)

    # Render DataFrame with chronological data.
    result_df = result_df.iloc[::-1]

    ax = result_df.plot(title=ticker, fontsize=12)
    ax.set_xlabel("Years")
    ax.set_ylabel("%")
    plt.show()

