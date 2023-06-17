import streamlit as st
import pandas as pd
import json
import pprint
from mftool import Mftool
import vectorbt as vbt
import quantstats as qs
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

def main():
    st.title("Mutual Fund Analyser")
    mf = Mftool()
    
    Mutual_Fund_Issuer_Name = st.text_input("Enter Mutual Fund Issuer Name", "uti nifty")
    if Mutual_Fund_Issuer_Name:
        results = mf.get_available_schemes(Mutual_Fund_Issuer_Name)
        st.write(results)
    
        Scheme_ID = st.text_input("Enter Scheme ID", "120716")
        if Scheme_ID:
            st.write(mf.get_scheme_details(Scheme_ID))

            data_string = mf.get_scheme_historical_nav(Scheme_ID,as_json=True)

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

            # Display the returns graph
            st.write(qs.plots.snapshot(returns, title='Portfolio performance'))

if __name__ == "__main__":
    main()
