import streamlit as st
import pandas as pd

st.title("📊 AI Financial Decision Support Agent")

st.write("Enter your financial data:")

income = st.number_input("Income ($)", min_value=0)
expenses = st.number_input("Expenses ($)", min_value=0)

if st.button("Analyze"):

    profit = income - expenses
    ratio = (expenses / income * 100) if income > 0 else 0

    st.subheader("📊 Financial Report")

    st.write(f"Total Income: ${income}")
    st.write(f"Total Expenses: ${expenses}")
    st.write(f"Profit: ${profit}")
    st.write(f"Expense Ratio: {ratio:.2f}%")

    st.subheader("💡 AI Recommendation")

    if ratio > 70:
        st.write("⚠️ Expenses are too high. Reduce unnecessary costs.")
    elif ratio > 50:
        st.write("⚠️ Try to control your spending.")
    else:
        st.write("✅ Good financial management. Keep it up!")