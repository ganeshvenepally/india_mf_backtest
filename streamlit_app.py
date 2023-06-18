# Import necessary libraries
import streamlit as st
from mftool import Mftool
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import logging

# Create a function to get and process data
def get_data():
    mf = Mftool()
    data_string = mf.get_scheme_historical_nav("125497",as_json=True)
    data = json.loads(data_string)
    df = pd.DataFrame(data['data'])
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df = df.sort_values(by='date', ascending=True)
    df['nav'] = df['nav'].astype(float)
    df.set_index('date', inplace=True)

    return df

# Create a function to create a portfolio
def create_portfolio(df):
    init_cash = 100000  # initial cash in account currency
    size = init_cash / df['nav'].iloc[0]  # number of shares to buy (invest the entire cash balance)

    # Create a vectorbt Portfolio
    portfolio = vbt.Portfolio.from_orders(
        df['nav'],  # price per share
        size,  # size of the order
        init_cash=init_cash,  # initial cash
        freq='D'  # set frequency to daily
    )

    return portfolio

def main():
    st.set_option('deprecation.showPyplotGlobalUse', False)  # Disable the warning
    st.title("Mutual Fund Analysis")
    df = get_data()
    portfolio = create_portfolio(df)
    returns = portfolio.returns()

    # Display the returns
    st.subheader('Returns')
    st.dataframe(returns)

    # Calculate and display statistics
    st.subheader('Statistics')
    stats = qs.reports.metrics(returns)
    st.dataframe(stats)

    # Display plots
    st.subheader('Plots')
    fig = qs.plots.snapshot(returns, title='Performance Snapshot')
    st.pyplot(fig)

    # Generate and display HTML report
    st.subheader('HTML Report')
    report_html = qs.reports.html(returns, output='html')
    st.markdown(report_html, unsafe_allow_html=True)

if __name__ == "__main__":
    # Suppress font not found warnings
    logging.getLogger('matplotlib.font_manager').setLevel(logging.CRITICAL)
    main()
