import streamlit as st
import yfinance as yf
st.title("📈 Market Trends: Silver")
data = yf.download("SLV", period="1y", progress=False)
if not data.empty:
    st.line_chart(data['Close'])
else:
    st.error("Could not fetch silver market data. Please try again later.")
csv=data.to_csv().encode('utf-8') 
st.download_button(label="Download Data", data=csv, file_name="silver_data.csv", mime="text/csv")
