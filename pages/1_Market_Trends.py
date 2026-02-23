import streamlit as st
import yfinance as yf
st.title("📈 Market Trends: Silver")
data = yf.download("SLV", period="1y", progress=False)
if not data.empty:
   average_price = data['Close'].rolling(20).mean().iloc[-1]
   current_price = data['Close'].iloc[-1]
   if current_price > average_price:
    st.warning(f"Current price (${current_price:.2f}) is above the 1-year average (${average_price:.2f}). Consider market trends before investing.")
   else:
    st.success("Current price is below the 1-year average. This could be a potential buying opportunity, but always consider market trends and do your research before investing.")   
   st.line_chart(data['Close'], height=300)
   csv=data.to_csv().encode('utf-8') 
   st.download_button(label="Download Data", data=csv, file_name="silver_data.csv", mime="text/csv")
else:
    st.error("Could not fetch silver data. Please try again later.")    
