import streamlit as st
import pprint
from mftool import Mftool
import pandas as pd
import vectorbt as vbt
import json
import quantstats as qs
import warnings
warnings.filterwarnings("ignore")
import os
import tempfile

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

            keepcharacters = (' ', '.', '_', '-')
            filename = f"{scheme_name} - VectorBT.html"
            filename = filename.replace("%", 'pct ')
            filename = "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

            # Save to a temporary file
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, filename)
            qs.reports.html(returns, title=f"{scheme_name}- VectorBT.html", file=temp_file)

            # Read the temporary file and create the download button
            with open(temp_file, 'r') as f:
                report_string = f.read()

            b64 = BytesIO(report_string.encode()).getvalue()
            st.download_button(label="Download Report", data=b64, file_name=filename, mime='text/html')

if __name__ == "__main__":
    main()
