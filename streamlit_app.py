import quantstats as qs

stock = qs.utils.download_returns('AAPL')
fig = qs.plots.snapshot(stock, title='AAPL Performance', show=False)
st.write(fig)
