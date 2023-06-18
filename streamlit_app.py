import streamlit as st
import pprint
from mftool import Mftool
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import matplotlib.pyplot as plt
from urllib.parse import quote

# Set Streamlit options
st.set_option('deprecation.showPyplotGlobalUse', False)

mf = Mftool()

# Input for Mutual Issuer Name
Mutual_Issuer_Name = st.text_input('Enter Mutual Issuer Name')

if Mutual_Issuer_Name:
    results = mf.get_available_schemes(Mutual_Issuer_Name)
    st.write(results)

    # Input for Scheme ID
    Scheme_ID = st.text_input('Enter Scheme ID')

    if Scheme_ID:
        scheme_details = mf.get_scheme_details(Scheme_ID)
        st.write(scheme_details)

        data_string = mf.get_scheme_historical_nav(Scheme_ID,as_json=True)
        scheme_name = scheme_details['scheme_name']

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
        keepcharacters = (' ', '.', '_', '-')
        filepath = f"{scheme_name} - VectorBT.html"
        filepath = filepath.replace("%", 'pct ')
        filepath = "".join(c for c in filepath if c.isalnum() or c in keepcharacters).rstrip()
        qs.reports.html(returns,  title=f"{scheme_name}- VectorBT.html" , output=filepath)

        # Provide a download link for the report
        st.markdown(f'[Download report]({quote(filepath)})')
