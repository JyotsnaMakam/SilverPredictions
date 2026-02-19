import streamlit as st
st.title("🧮 Silver Investment Calculator")
price_per_gram = st.number_input("Enter current silver price per gram (USD)", min_value=0.0, value=92.5)
budget=st.number_input("Your Budget (rs)", min_value=0.0, value=100000.0)
if price_per_gram>0:
    total_silver=budget/price_per_gram
    st.success(f"With {budget} INR, you can buy approximately {total_silver:.2f} grams of silver")
