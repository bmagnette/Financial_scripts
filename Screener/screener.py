from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
from stem import Signal
from stem.control import Controller
from torrequest import TorRequest

accountant = ['cash-flow', 'balance-sheet', 'financials']
tickers_list = ['OSI.PA']
marketplace = 'PAR'
start = datetime.now()

pays = ['USA' 'Australia' 'Indonesia' 'Germany' 'France' 'Canada' 'Belgium'
 'Argentina' 'United Kingdom''Malaysia' 'Netherlands' 'Switzerland'
 'Taiwan' 'Norway' 'Sweden' 'Denmark' 'Austria' 'Brazil' 'Singapore'
 'India' 'Mexico' 'Hong Kong' 'New Zealand' 'Spain' 'Ireland' 'Russia'
 'Italy' 'Greece' 'Portugal' 'Israel' 'Turkey' 'Estonia' 'Thailand'
 'Finland' 'Iceland' 'Latvia' 'South Korea' 'Lithuania' 'Qatar' 'China'
 'Venezuela']


def get_financial(company):
    """
    Request the financial information from Yahoo Finance
    :return: Dataframe with all financial information
    """

    financial_df = pd.DataFrame()
    writer = pd.ExcelWriter('XLS/{}.xlsx'.format(company))

    for elements_financier in accountant:
        r = requests.get("https://fr.finance.yahoo.com/quote/{}/{}?p={}".format(company, elements_financier, ticker))
        if r.status_code != 200: print(r.status_code, ":", r.reason)

        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all('table')

        df = pd.DataFrame()
        raw = []

        for table in tables:
            tr = table.find_all('tr')
            for row in tr:
                td = row.find_all('td')

                # Catch if this is a title
                if len(td) == 1:
                    data = str(td[0].find(text=True))
                    raw.append(data)
                    df = df.append([raw])
                    raw = []
                    continue

                # Add a line with a temporary raw
                for element in td:
                    data = str(element.find(text=True))
                    raw.append(data)
                df = df.append([raw])
                del raw[:]
        df.set_index([0], inplace=True)
        df.to_excel(writer, elements_financier)
        financial_df = pd.concat([financial_df, df])
    writer.save()
    print("########{}########".format(company))
    return financial_df


def get_summary(company):
    """
    Get additional information on company
    :return: Summary DataFrame
    """
    summary_info = pd.DataFrame()
    raw = []
    r = requests.get("https://fr.finance.yahoo.com/quote/{}?p={}".format(company, company))
    if r.status_code != 200: print(r.status_code, ":", r.reason)

    soup = BeautifulSoup(r.text, "lxml")
    tables = soup.find_all('table')

    for table in tables:
        spans = table.find_all('span')
        for element in spans:
            raw.append(element.get_text())
            if len(raw) == 2:
                summary_info = summary_info.append([raw])
                del raw[:]

    summary_info.set_index(summary_info.iloc[:, 0], inplace=True)
    return summary_info


def compute_financial(financial_info, summary_info):
    """
    Compute ratio depending of financial information
    :return: If company verify the ratio
    """
    caf, benefice, long_debt, investment, cash, capitalisation, ebit = get_raw(financial_info, summary_info)

    investment = investment.apply(cleaner)
    cash = cash.apply(cleaner)
    long_debt = long_debt.apply(cleaner)
    ebit = ebit.apply(cleaner)
    caf = caf.apply(cleaner)

    try:
        enterprise_value = int(capitalisation) + int(long_debt.iloc[0]) - int(investment.iloc[0]) - int(cash.iloc[0])
        print("Capitalisation : ", capitalisation)
        print("EV :", enterprise_value)
        print("EBIT :", ebit.iloc[0])
        print("CAF :", caf.iloc[0])
        print("DEBT", long_debt.iloc[0])

    except ValueError:
        print(long_debt.iloc[0], investment.iloc[0], cash.iloc(0))


def get_raw(financial_info, summary_info):
    capitalisation = cleaner2(summary_info.loc['Cap. boursière', 1])
    caf = financial_info.loc['Flux total de trésorerie des activités d’exploitation']
    ebit = financial_info.loc['Bénéfice ou perte d’exploitation']
    benefice = financial_info.loc['Bénéfice net']
    long_debt = financial_info.loc['Dette à long terme']
    investment = financial_info.loc['Investissements']
    cash = financial_info.loc['Espèces et quasi-espèces']

    return caf, benefice, long_debt, investment, cash, capitalisation, ebit


def cleaner(x):
    try:
        x = x.replace("\xa0", '')
        if len(x) == 1:
            x = 0
        return x
    except AttributeError:
        print("AttributeError : Empty table N°")


def cleaner2(x):
    if 'M' in x:
        x = x[:-1]
        x = x.replace(",", '')
    elif 'B' in x:
        x = x[:-1]
        x = x.replace(",", '')
        x = x + '000'
    return x


def select_company():
    main_company = pd.read_excel('XLS/yahoo_tickers.xlsx', sheet_name='Stock', skiprows=3)
    df_companies = main_company[main_company['Exchange'] == marketplace]
    print("Start the scrapping for ", len(df_companies))
    list_tickers = df_companies['Ticker'].tolist()
    return list_tickers


def get_tor_session():
    s = requests.session()
    # Tor uses the 9050 port as the default socks port
    s.proxies = {'http':  'socks5://127.0.0.1:9150',
                       'https': 'socks5://127.0.0.1:9150'}
    return s


# signal TOR for a new connection
def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="password")
        controller.signal(Signal.NEWNYM)


if __name__ == '__main__':
    session = get_tor_session()
    print(session.get("http://httpbin.org/ip").text)
    # Above should print an IP different than your public IP
    # Following prints your normal public IP
    print(requests.get("http://httpbin.org/ip").text)
    renew_connection()
    session = get_tor_session()
    print(session.get("http://httpbin.org/ip").text)

    """list_companies = select_company()
    for ticker in list_companies:
        try:
            financial = get_financial(session, ticker)
            summary = get_summary(session, ticker)
            compute_financial(financial, summary)
        except KeyError:
            print("KeyError : Ticker doesn't exist anymore.")"""

