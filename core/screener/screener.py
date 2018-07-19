from typing import Any

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from torrequest import TorRequest
import time
import logging

accountant = ['cash-flow', 'balance-sheet', 'financials']
marketplace = 'PAR'
url = "https://fr.finance.yahoo.com/quote/"


def get_financial(tor: TorRequest, company: str) -> pd.DataFrame:
    """
    Get accountability information on company
    """

    financial_df = pd.DataFrame()
    # writer = pd.ExcelWriter('XLS/{}.xlsx'.format(company))

    for elements_financier in accountant:
        r = tor.get(url + "{}/{}?p={}".format(company, elements_financier, company))
        if r.status_code != 200:
            print(r.status_code, ":", r.reason)
            time.sleep(10)
            financial_df = get_financial(tor, company)
            return financial_df

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
        # df.to_excel(writer, elements_financier)
        financial_df = pd.concat([financial_df, df])
    # writer.save()
    return financial_df


def get_summary(tor: TorRequest, company: str) -> pd.DataFrame:
    """
    Get additional information on company
    """
    summary_info = pd.DataFrame()
    raw = []
    r = tor.get(url + "{}?p={}".format(company, company))
    if r.status_code != 200:
        print(r.status_code, ":", r.reason)

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


def compute_financial(financial_info, summary_info, ticker):
    """
    Compute ratio depending of financial information
    """
    caf, benefice, long_debt, investment, cash, capitalisation, ebit, cap_display, cp = get_raw(financial_info,
                                                                                                summary_info, '2017')

    # Calcul
    enterprise_value = float(capitalisation) + long_debt - investment - cash

    caf_debt = caf / long_debt
    ev_ebit = enterprise_value / ebit

    return_on_requity = benefice / cp

    if 0 <= ev_ebit <= 10.0 and caf_debt <= 5.0 and return_on_requity >= 0.1:
        print("########{}########".format(ticker))
        print("Capitalisation : ", cap_display)
        print("EV : ", enterprise_value)
        print("EBIT :", ebit)
        print("EV/EBIT :", ev_ebit)
        print("CAF/DEBT :", caf_debt)
        print("ROE :", return_on_requity)
        # print("ROIC : ")


def get_raw(financial_info: pd.DataFrame, summary_info: pd.DataFrame, year):
    annee = 0

    if financial_info.iloc[:, 0].str.match("0").count() >= 10:
        annee = 2

    financial_info.iloc[1:, :] = financial_info.iloc[1:, :].applymap(cleaner)
    capitalisation = cleaner2(summary_info.loc['Cap. boursière', 1])
    cap_display = summary_info.loc['Cap. boursière', 1]
    caf = financial_info.loc['Flux total de trésorerie des activités d’exploitation', annee]
    ebit = financial_info.loc['Bénéfice ou perte d’exploitation', annee]
    benefice = financial_info.loc['Bénéfice net', annee]
    benefice = benefice.iloc[0]
    long_debt = financial_info.loc['Dette à long terme', annee]
    investment = financial_info.loc['Investissements', annee]
    cash = financial_info.loc['Espèces et quasi-espèces', annee]
    cp = financial_info.loc['Total des capitaux propres', annee]

    return caf, benefice, long_debt, investment, cash, capitalisation, ebit, cap_display, cp


def cleaner(x: Any) -> float:
    x = str(x).replace("\xa0", '')
    if len(x) == 1 or str(x) == "None" or "/" in str(x):
        x = 0
    return float(x)


def cleaner2(x: Any) -> float:
    if 'M' in x:
        x = x[:-1]
        x = x.replace(",", '')
    elif 'B' in x:
        x = x[:-1]
        x = x.replace(",", '')
        x = x + '000'
    return float(x)


def select_company() -> list:
    print(datetime.now().strftime("%H:%M:%S"), "### SELECT COMPANIES FROM XLSX ###")
    main_company = pd.read_excel('XLS/yahoo_tickers.xlsx', sheet_name='Stock', skiprows=3)
    df_companies = main_company[main_company['Exchange'] == marketplace]
    print("Start the scrapping for ", len(df_companies))
    list_tickers = df_companies['Ticker'].tolist()
    return list_tickers


if __name__ == '__main__':
    nb_requests, analyzed, error = 0, 0, 0
    keyerror_list, valuerror_list, indexerror_list, zerodivision_list = [], [], [], []
    list_companies = select_company()
    with TorRequest(proxy_port=9150, ctrl_port=9051, password='password') as tr:
        # Making 4 requests by company
        for ticker in list_companies:
            try:
                print(ticker)
                nb_requests += 4
                analyzed += 1
                financial = get_financial(tr, ticker)
                summary = get_summary(tr, ticker)
                compute_financial(financial, summary, ticker)
                if nb_requests >= 75:
                    nb_requests = 0

                    r1 = tr.get('http://ipecho.net/plain')
                    tr.reset_identity()
                    r2 = tr.get('http://ipecho.net/plain')
                    print("-----------")
                    print(analyzed, "/", len(list_companies), " : ", datetime.now().strftime("%H:%M:%S"))
                    print(r1.text, "---->", r2.text)
                    print("Error : ", error / analyzed)
                    print("-----------")
            except KeyError:
                error += 1
                keyerror_list.append(ticker)
                # print("KeyError : Ticker doesn't exist anymore.")
            except ZeroDivisionError:
                error += 1
                zerodivision_list.append(ticker)
                # print("ZeroDivisionError : DEBT or EBIT null")
            except ValueError:
                error += 1
                valuerror_list.append(ticker)
                # print("ValueError : Empty")
            except IndexError:
                indexerror_list.append(ticker)
                error += 1
                # print("IndexError : Empty")
    print("KeyError : ", keyerror_list)
    print("ZeroDivisionError : ", zerodivision_list)
    print("ValueError : ", valuerror_list)
    print("IndexError : ", indexerror_list)
