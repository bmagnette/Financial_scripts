import pandas as pd
import requests
import json
from constants import DIR_PATH

url_api = "https://lestransactions.fr/api"

position = ['Holding', 'Administrateur', 'CFO', 'Directeur', 'Dirigeant', 'Gérant']
nature = ['Cession', 'Acquisition']


def fct(x):
    x = x.split(',')[0]
    return x


def get_api_transaction_data(**args)-> pd.DataFrame():
    """ Get french insiders transactions via lestransactions.fr """
    resp = requests.get(url_api, data=args)

    if resp.status_code is 200:
        data = resp.text
        print(data)
    else:
        print(resp.status_code, resp.reason)


def get_excel_transaction_data(**args)-> pd.DataFrame():
    excel_data = pd.read_csv(DIR_PATH + "/core/analyze/data/data.csv", error_bad_lines=False, sep=';', header=1)

    for k, v in args.items():
        excel_data = excel_data[excel_data[k].str.contains(v)]

    return excel_data


def analyze(df: pd.DataFrame())-> pd.DataFrame():
    df.loc[:, 'Déclarant'].apply(fct)

    acquisition = df[df['Nature'] == 'Acquisition'].groupby(['Déclarant'])['Volume'].sum()
    cession = df[df['Nature'] == 'Cession'].groupby(['Déclarant'])['Volume'].sum()
    print("### Acquisition ###")
    print(acquisition)

    print("### cession ###")
    print(cession)


if __name__ == '__main__':
    get_api_transaction_data(isin="FR0004152882")

    # Columns = Prix, Nature, Instrument, Volume, Total, Date, Déclarant, Société, ISIN
    #main_df = get_excel_transaction_data(ISIN="FR0004152882", Déclarant="Hugues")



