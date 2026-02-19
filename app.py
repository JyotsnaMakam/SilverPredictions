import streamlit as st
import pickle
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from chatbot import PrecisousMetalsBot
import warnings
warnings.filterwarnings('ignore', category=Warning)

# 1. Page Setup
st.set_page_config(page_title="Gold & Silver Intelligence", page_icon="💰", layout="wide")

# 2. Load Model Safely
@st.cache_resource
def load_model():
 with open('silver_model.pkl', 'rb') as file:
  return pickle.load(file)

silver_model = load_model()

# Initialize chatbot
@st.cache_resource
def load_chatbot():
 return PrecisousMetalsBot()

bot = load_chatbot()

# Initialize chat history
if "chat_history" not in st.session_state:
 st.session_state.chat_history = []
# page for simple multi-page navigation: 'main' or 'city'
if "page" not in st.session_state:
  st.session_state.page = "main"

def go_to_city():
  st.session_state.page = "city"

def go_back():
  st.session_state.page = "main"

# 3. Sidebar Inputs
st.sidebar.header("📊 Settings")
amount_inr = st.sidebar.number_input("Investment (INR):", min_value=0, value=100000)

# 4. Fetch Market Data
with st.spinner('Fetching latest market prices...'):
 # Fetch ETF data
 silv_data = yf.download("SLV", period="30d", progress=False)
 gold_data = yf.download("GLD", period="30d", progress=False)
 
 # Fetch commodity futures prices (more accurate spot prices)
 try:
  gc_data = yf.download("GC=F", period="5d", progress=False)  # Gold futures
  si_data = yf.download("SI=F", period="5d", progress=False)  # Silver futures
 except:
  gc_data = None
  si_data = None

# Get Current Prices from ETFs
cur_gld_etf = gold_data['Close'].iloc[-1].item()
if not silv_data.empty:
 cur_slv_etf = silv_data['Close'].iloc[-1].item()
else:
  st.error("Could not fetch latest silver Data.Please try again later.")
  st.stop()

# Get SPOT prices (USD per troy ounce) from futures - if available
if gc_data is not None and len(gc_data) > 0:
 # GC futures price is per 100 oz, so divide by 100 to get per oz
 cur_gold_spot_usd = gc_data['Close'].iloc[-1].item() / 100
else:
 # Fallback: Since GLD = 0.1 oz per share, multiply by 10 to get per oz
 cur_gold_spot_usd = cur_gld_etf * 10

if si_data is not None and len(si_data) > 0:
 # SI futures price is per 5000 oz, so divide by 5000 to get per oz
 cur_silver_spot_usd = si_data['Close'].iloc[-1].item() / 5000
else:
 # Fallback: SLV = 1 oz per share
 cur_silver_spot_usd = cur_slv_etf

# Get 10-Day Highs
max_silv_10 = silv_data['High'].tail(10).max().item()
max_gold_10 = gold_data['High'].tail(10).max().item()

# Gold-to-Silver Ratio (using spot prices)
gs_ratio = cur_gold_spot_usd / cur_silver_spot_usd

# Calculate Purchasing Power (USD to INR conversion: 1 USD = 91.09 INR)
# Based on: 1 Lakh INR (100,000) = 1,097.80 USD
usd_inr_rate = 91.09
amount_usd = amount_inr / usd_inr_rate

# Conversion factor: 1 troy ounce = 31.1035 grams
troy_oz_to_grams = 31.1035

# Calculate gold and silver in grams based on SPOT prices
# cur_gold_spot_usd = USD per troy ounce
# cur_silver_spot_usd = USD per troy ounce
silver_grams = (amount_usd / cur_silver_spot_usd) * troy_oz_to_grams
gold_grams = (amount_usd / cur_gold_spot_usd) * troy_oz_to_grams

# Calculate Gold Prices for Different Karats
# cur_gold_spot_usd is the spot gold price in USD per troy ounce
gold_price_per_gram_usd = cur_gold_spot_usd / troy_oz_to_grams  # $ per gram for 24K

# Calculate prices for different karats
gold_24k_usd = gold_price_per_gram_usd  # 100% pure
gold_22k_usd = gold_price_per_gram_usd * (22/24)  # 91.67% pure
gold_18k_usd = gold_price_per_gram_usd * (18/24)  # 75% pure

# Convert to INR
gold_24k_inr = gold_24k_usd * usd_inr_rate
gold_22k_inr = gold_22k_usd * usd_inr_rate
gold_18k_inr = gold_18k_usd * usd_inr_rate

# Display Investment Breakdown in Sidebar
st.sidebar.divider()
st.sidebar.subheader("💼 Your Investment Breakdown")

if amount_inr > 0:
 st.sidebar.metric("💵 Investment Amount (INR)", f"₹{amount_inr:,.0f}")
 st.sidebar.metric("💵 Investment Amount (USD)", f"${amount_usd:,.2f}")
 
 # Show current prices for reference
 st.sidebar.write("---")
 st.sidebar.write("**📈 ETF Prices:**")
 st.sidebar.write(f"🥈 SLV: ${cur_slv_etf:.2f}/share")
 st.sidebar.write(f"🥇 GLD: ${cur_gld_etf:.2f}/share")
 
 st.sidebar.write("---")
 st.sidebar.write("**📊 Spot Prices (Per Troy Ounce):**")
 st.sidebar.write(f"🥈 Silver: ${cur_silver_spot_usd:.2f}/oz")
 st.sidebar.write(f"🥇 Gold: ${cur_gold_spot_usd:.2f}/oz")
 
 st.sidebar.write("---")
 st.sidebar.write(f"**Per Gram (USD):** ${gold_price_per_gram_usd:.2f}")
 st.sidebar.write(f"**Per Gram (INR):** ₹{gold_24k_inr:.2f}")
 
 st.sidebar.write("---")
 st.sidebar.write("**📊 You can buy:**")
 
 col_silv, col_gold = st.sidebar.columns(2)
 with col_silv:
  st.metric("🥈 Silver Grams", f"{silver_grams:.2f} g", "(≈1oz/share)", delta_color="off")
 with col_gold:
  st.metric("🥇 Gold Grams", f"{gold_grams:.2f} g", "(≈0.1oz/share)", delta_color="off")
else:
 st.sidebar.info("💡 Enter an investment amount to see purchasing power")

# 5. Main Dashboard UI
st.title("💰 Precious Metals Dashboard")
st.write(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
st.divider()

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Silver (Spot Price)", f"${cur_silver_spot_usd:.2f}/oz")
m2.metric("Silver 10D High", f"${max_silv_10:.2f}")
m3.metric("Gold (Spot Price)", f"${cur_gold_spot_usd:.2f}/oz")
m4.metric("Gold/Silver Ratio", f"{gs_ratio:.1f}")

st.divider()

# 6. Prediction & Strategy
col1, col2 = st.columns(2)

with col1:
 st.subheader("🥈 Silver AI Prediction")
 if st.button("Run Silver AI Forecast", use_container_width=True):
# UNIVERSAL FIX: Handles arrays, lists, or single numbers
  prediction_raw = silver_model.predict([[cur_silver_spot_usd]])

# Flatten the result to a single float
  if isinstance(prediction_raw, (np.ndarray, list)):
   pred_val = float(prediction_raw.ravel()[0])
  else:
   pred_val = float(prediction_raw)

  if pred_val > cur_silver_spot_usd:
   st.success(f"✅ RECOMMENDATION: BUY SILVER")
   st.write(f"AI Target Price: **${pred_val:.2f}**")
   st.balloons()
  else:
   st.error(f"❌ RECOMMENDATION: HOLD/SELL")
   st.write(f"AI Target Price: **${pred_val:.2f}**")

with col2:
 st.subheader("💡 Market Insight")
 if gs_ratio > 80:
  st.info("The Gold/Silver ratio is high (>80). Silver is historically cheap compared to Gold. This favors Silver accumulation.")
 elif gs_ratio < 60:
  st.warning("The Gold/Silver ratio is low (<60). Gold is currently showing more relative strength than Silver.")
 else:
  st.write("The ratio is in a neutral zone. Follow individual price targets.")

# 7. Charts
st.subheader("📈 30-Day Trend Comparison")
# Ensure equal length by taking minimum length
min_len = min(len(silv_data), len(gold_data))
chart_data = {
 'Silver Price': silv_data['Close'][:min_len].values.reshape(-1),
 'Gold Price': gold_data['Close'][:min_len].values.reshape(-1)
}
chart_df = pd.DataFrame(chart_data)
st.line_chart(chart_df)

# 8. Chatbot Section (Non-Disruptive)
st.divider()
st.subheader("🤖 Ask Our Investment Advisor Bot")

# Display chat history
for message in st.session_state.chat_history:
 with st.chat_message(message["role"]):
  st.write(message["content"])

# Chat input
user_input = st.chat_input("Ask about silver, gold, investments, or market trends...")

if user_input:
 # Add user message to history
 st.session_state.chat_history.append({"role": "user", "content": user_input})
 
 # Get bot response
 bot_response = bot.get_response(user_input)
 st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
 
 # Rerun to display new messages
 st.rerun()

# Suggested questions
if len(st.session_state.chat_history) == 0:
 st.info("💡 Try asking: What is silver?What is gold? How to invest? Gold vs Silver? Market trends?")

# Page navigation: Proceed button to go to city selector
if st.session_state.page == "main":
  st.write("\n")
  if st.button("Proceed", use_container_width=True):
    go_to_city()

elif st.session_state.page == "city":
  st.header("Select City for Local Silver Price")
  # compute silver per gram in INR
  silver_price_per_gram_usd = cur_silver_spot_usd / troy_oz_to_grams
  silver_price_per_gram_inr = silver_price_per_gram_usd * usd_inr_rate

  # Example city premiums (fixed INR per gram) - adjust as needed
  city_premium_inr = {
    "Mumbai": 20.0,
    "Delhi": 15.0,
    "Bengaluru": 10.0,
    "Chennai": 12.0,
    "Kolkata": 18.0,
    "Hyderabad": 14.0,
    "Pune": 9.0,
    "Ahmedabad": 22.0,
    "Surat": 16.0,
    "Jaipur": 13.0
  }

  city = st.selectbox("Choose city:", list(city_premium_inr.keys()))

  # Calculate city silver price per gram (INR) using base + fixed premium
  premium = city_premium_inr.get(city, 0.0)
  price_inr = silver_price_per_gram_inr + premium

  # Display base, premium and final price
  st.write(f"Base silver price (INR/g): ₹{silver_price_per_gram_inr:,.2f}")
  st.write(f"Local premium for {city}: ₹{premium:.2f}/g")
  st.text_input(f"Silver price in {city} (INR/gram)", value=f"₹{price_inr:,.2f}")

  if st.button("Back to Dashboard"):
    go_back()
