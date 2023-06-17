import streamlit as st
import pprint
from mftool import Mftool
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import warnings
import base64

warnings.filterwarnings("ignore")

def main():
    st.title("Mutual Fund Analysis")

    mf = Mftool()

    Mutual_Fund_Issuer_Name = st.text_input("Enter Mutual Fund Issuer Name", "uti nifty")

    if Mutual_Fund_Issuer_Name:
        results = mf.get_available_schemes(Mutual_Fund_Issuer_Name)
        st.write(results)

        Scheme_ID = st.text_input("Enter Scheme ID", "120716")

        if Scheme_ID:
            scheme_details = mf.get_scheme_details(Scheme_ID)
            st.write(scheme_details)

            data_string = mf.get_scheme_historical_nav(Scheme_ID,as_json=True)

            scheme_name = mf.get_scheme_details(Scheme_ID)['scheme_name']

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

            report_html = qs.reports.html(returns, title=f"{scheme_name}- VectorBT.html")

            b64 = base64.b64encode(report_html.encode()).decode()  # some strings <-> bytes conversions necessary here
            href = f'<a href="data:text/html;base64,{b64}" download="{scheme_name}.html">Download HTML Report</a>'
            
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
