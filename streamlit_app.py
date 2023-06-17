# Necessary imports
from mftool import Mftool
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import streamlit as st

# Streamlit title
st.title('Mutual Fund Analysis')

# function to calculate statistics
def calculate_statistics(scheme_id):
    mf = Mftool()

    data_string = mf.get_scheme_historical_nav(scheme_id,as_json=True)

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

    # Now use QuantStats to calculate various statistics
    return qs.reports.html(returns)

# User input for scheme_id
scheme_id = st.text_input("Enter scheme id", "125497")

# Call calculate_statistics function when button is pressed
if st.button('Calculate Statistics'):
    st.markdown(calculate_statistics(scheme_id), unsafe_allow_html=True)
