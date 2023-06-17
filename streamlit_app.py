import streamlit as st
import pprint
from mftool import Mftool
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

st.title('Mutual Fund Analysis')

mf = Mftool()

# Get input from user using Streamlit
Mutual_Fund_Issuer_Name = st.text_input("Enter Mutual Fund Issuer Name", 'uti nifty')

if Mutual_Fund_Issuer_Name:
    results = mf.get_available_schemes(Mutual_Fund_Issuer_Name)
    st.write(results)

# Get input from user using Streamlit
Scheme_ID = st.text_input("Enter Scheme ID", '120716')

if Scheme_ID:
    details = mf.get_scheme_details(Scheme_ID)
    st.write(details)

    data_string = mf.get_scheme_historical_nav(Scheme_ID, as_json=True)
    scheme_name = mf.get_scheme_details(Scheme_ID)['scheme_name']

    # Parse the string into a dictionary
    data = json.loads(data_string)

    # Convert data to dataframe
    df = pd.DataFrame(data['data'])

    # Convert date string to datetime and sort by date
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df = df.sort_values(by='date', ascending=True)

    # Convert nav to float and set date as index
    df['nav'] = df['nav'].astype(float)
    df.set_index('date', inplace=True)

    # Initialize the portfolio by investing the entire cash balance in the asset
    init_cash = 100000  # initial cash in account currency
    size = init_cash / df['nav'].iloc[0]  # number of shares to buy (invest the entire cash balance)

    # Create a vectorbt Portfolio
    portfolio = vbt.Portfolio.from_orders(
        df['nav'],  # price per share
        size,  # size of the order
        init_cash=init_cash,  # initial cash
        freq='D'  # set frequency to daily
    )

    # Calculate daily returns of the portfolio
    returns = portfolio.returns()

    # Export Quantstats HTML Report
    qs.reports.html(returns,  title=f"{scheme_name} - VectorBT.html" , output=filepath, download_filename=filepath)
    
    st.markdown(get_table_download_link(returns), unsafe_allow_html=True)
    
def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings
    href = f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'
    return href
