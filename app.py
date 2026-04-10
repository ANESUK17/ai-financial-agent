import streamlit as st
import pandas as pd
import plotly.express as px

# Financial Dashboard App
st.title('Comprehensive Financial Dashboard')

# Sidebar navigation
st.sidebar.title('Navigation')
option = st.sidebar.selectbox('Choose a section:', ['Budget', 'Goals', 'Analysis', 'Health', 'Projections'])

# Session state to hold user data
if 'data' not in st.session_state:
    st.session_state.data = {}

# 1. Budget Categories
if option == 'Budget':
    st.header('Budget Categories')
    categories = st.multiselect('Select categories', ['Rent', 'Groceries', 'Utilities', 'Transport', 'Entertainment'])
    expenses = [1000, 300, 150, 200, 100]  # Example expenses
    df = pd.DataFrame({'Categories': categories, 'Expenses': expenses})
    fig = px.pie(df, values='Expenses', names='Categories', title='Expenses by Category')
    st.plotly_chart(fig)

# 2. Time Period Toggle
    period = st.selectbox('Select time period', ['Daily', 'Weekly', 'Monthly', 'Yearly'])
    # Logic to handle time period can be added later.

# 3. Financial Goals
elif option == 'Goals':
    st.header('Set Financial Goals')
    target = st.number_input('Savings Target', min_value=0)
    current_savings = st.number_input('Current Savings', min_value=0)
    progress = (current_savings / target) * 100 if target > 0 else 0
    st.progress(progress)

# 4. Historical Data
elif option == 'Analysis':
    st.header('Historical Data')
    data = {'Date': ['2026-01-01', '2026-02-01'], 'Savings': [1000, 1500]}
    df = pd.DataFrame(data)
    st.write(df)
    st.download_button('Download Data as CSV', df.to_csv().encode('utf-8'), 'data.csv', 'text/csv')

# 5. Debt Analysis
elif option == 'Health':
    st.header('Debt Analysis')
    income = st.number_input('Monthly Income', min_value=0)
    debt = st.number_input('Total Debt', min_value=0)
    ratio = (debt / income) * 100 if income > 0 else 0
    st.write(f'Debt-to-Income Ratio: {ratio:.2f}%')

# Additional sections: Emergency Fund Calculator, Projections, Financial Health Score, Comparison Mode...

# 6. Emergency Fund Calculator
elif option == 'Projections':
    st.header('Emergency Fund Calculator')
    months = st.selectbox('Select months', [3, 6, 12])
    monthly_expense = st.number_input('Monthly Expense', min_value=0)
    emergency_fund = monthly_expense * months
    st.write(f'Emergency Fund Needed: ${emergency_fund}')

# Placeholder for an Actionable AI Recommendations function
st.sidebar.success('Check your financial dashboard sections!')

