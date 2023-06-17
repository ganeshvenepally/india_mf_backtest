import streamlit as st
import pprint
from mftool import Mftool
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import matplotlib.pyplot as plt
import warnings
import os
import tempfile
from io import BytesIO
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
            
            # Plot returns
            plt.figure(figsize=[10,5])
            qs.plots.returns(returns, cumulative=True, logy=True)
            plt.title(f"Returns for {scheme_name}")

            # Save figure to a BytesIO object
            buf = BytesIO()
            plt.savefig(buf, format="png")
            # Embed the result in the html output.
            data = base64.b64encode(buf.getbuffer()).decode("utf8")
            st.markdown(f'<img src="data:image/png;base64,{data}" />', unsafe_allow_html=True)

            st.download_button(
                "Download image",
                data=buf.getvalue(),
                file_name=f"{scheme_name}.png",
                mime="image/png",
            )

if __name__ == "__main__":
    main()
