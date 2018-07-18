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


def get_transaction_data(**args)-> pd.DataFrame():
    """ Get french insiders transactions via lestransactions.fr """
    resp = requests.get(url_api, params=args)

    if resp.status_code is 200:
        data = json.loads(resp.text)
        print(data)
    else:
        print(resp.status_code, resp.reason)


def analyze():
    print("")


if __name__ == '__main__':
    #get_transaction_data(isin="FR0004152882")

    test = pd.read_csv(DIR_PATH + "/data/data.csv", error_bad_lines=False, sep=';', header=1)
    df = test[test['ISIN'] == 'FR0010465534']

    df.loc[:, 'Déclarant'].apply(fct)

    acquisition = df[df['Nature'] == 'Acquisition']
    cession = df[df['Nature'] == 'Cession']

    acquisition = acquisition.groupby(['Déclarant'])['Volume'].sum()
    cession = cession.groupby(['Déclarant'])['Volume'].sum()

    print("### Acquisition ###")
    print(acquisition)

    print("### cession ###")
    print(cession)
