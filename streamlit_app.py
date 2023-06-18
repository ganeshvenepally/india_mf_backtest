import streamlit as st
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import matplotlib.pyplot as plt
import warnings
from mftool import Mftool

warnings.filterwarnings("ignore")

st.title('Mutual Fund Analysis')

# User input
Mutual_Issuer_Name = st.text_input('Enter Mutual Issuer Name', 'uti nifty')
Scheme_ID = st.text_input('Enter Scheme ID', '120716')

mf = Mftool()

if st.button('Analyze'):
    st.subheader('Scheme Details')
    scheme_details = mf.get_scheme_details(Scheme_ID)
    st.write(scheme_details)

    st.subheader('Historical NAV Data and Portfolio Returns')
    data_string = mf.get_scheme_historical_nav(Scheme_ID, as_json=True)
    data = json.loads(data_string)
    df = pd.DataFrame(data['data'])
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df = df.sort_values(by='date', ascending=True)
    df['nav'] = df['nav'].astype(float)
    df.set_index('date', inplace=True)

    init_cash = 100000
    size = init_cash / df['nav'].iloc[0]

    portfolio = vbt.Portfolio.from_orders(
        df['nav'],
        size,
        init_cash=init_cash,
        freq='D'
    )

    returns = portfolio.returns()
    st.line_chart(returns)

    st.subheader('Quantstats Report')
    report = qs.reports.html(returns, output='htmlstring')
    st.components.v1.html(report, height=800, scrolling=True)
