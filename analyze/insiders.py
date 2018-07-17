import pandas as pd

url = "C:/Users/Pierre/PycharmProjects/Financial_scripts/analyze/data/data.csv"


def fct(x):
    x = x.split(',')[0]
    return x


if __name__ == '__main__':
    test = pd.read_csv(url, error_bad_lines=False, sep=';', header=1)
    df = test[test['ISIN'] == 'FR0010465534']
    df['Déclarant'] = df['Déclarant'].apply(fct)

    acquisition = df[df['Nature'] == 'Acquisition']
    cession = df[df['Nature'] == 'Cession']

    acquisition = acquisition.groupby(['Déclarant'])['Volume'].sum()
    cession = cession.groupby(['Déclarant'])['Volume'].sum()

    print("### Acquisition ###")
    print(acquisition)

    print("### cession ###")
    print(cession)
