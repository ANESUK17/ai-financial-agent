import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="AI Financial Agent", layout="wide")

st.title("📊 AI Financial Decision Support Agent")

st.write("Enter your financial data:")

col1, col2 = st.columns(2)

with col1:
    income = st.number_input("Income ($)", min_value=0, value=0)

with col2:
    expenses = st.number_input("Expenses ($)", min_value=0, value=0)

# Input Validation
if income < 0 or expenses < 0:
    st.error("❌ Please enter positive values")
elif income == 0 and expenses > 0:
    st.warning("⚠️ You have expenses but no income. Please enter income data.")
elif expenses > income:
    st.warning("⚠️ Warning: Your expenses exceed your income!")

if st.button("Analyze", type="primary"):
    
    if income == 0:
        st.error("❌ Please enter income to calculate expense ratio")
    else:
        profit = income - expenses
        savings = profit
        ratio = (expenses / income * 100)
        savings_ratio = (savings / income * 100)

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Income", f"${income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${expenses:,.2f}")
        with col3:
            st.metric("Profit/Savings", f"${profit:,.2f}", delta=f"{savings_ratio:.1f}% of income")
        with col4:
            st.metric("Expense Ratio", f"{ratio:.2f}%")

        # Data Visualization
        st.subheader("📊 Financial Breakdown")
        
        fig = go.Figure(data=[
            go.Bar(name='Income', x=['Financial Summary'], y=[income], marker_color='#00CC96'),
            go.Bar(name='Expenses', x=['Financial Summary'], y=[expenses], marker_color='#EF553B')
        ])
        
        fig.update_layout(
            barmode='group',
            height=400,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Pie Chart for Expense Breakdown
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Expenses', 'Savings'],
            values=[expenses, savings],
            marker=dict(colors=['#EF553B', '#00CC96']),
            hole=.3
        )])
        
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

        # AI Recommendation
        st.subheader("💡 AI Recommendation")

        if ratio > 90:
            st.error("🚨 Critical: Expenses are 90%+ of income! You're spending almost all you earn. Take immediate action to reduce costs.")
        elif ratio > 70:
            st.warning("⚠️ Expenses are too high (70%+). Reduce unnecessary costs and prioritize essential spending.")
        elif ratio > 50:
            st.info("⚠️ Try to control your spending. Aim for expenses below 50% to build wealth.")
        else:
            st.success("✅ Excellent financial management! You're saving more than half your income. Keep it up!")

        # Additional Financial Metrics
        st.subheader("📈 Financial Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Savings Rate:** {savings_ratio:.2f}%")
            st.write(f"**Monthly Savings:** ${savings:,.2f}")
        
        with col2:
            if income > 0:
                months_to_save_1k = 1000 / savings if savings > 0 else float('inf')
                if months_to_save_1k != float('inf'):
                    st.write(f"**Months to save $1,000:** {months_to_save_1k:.1f}")
                else:
                    st.write("**Months to save $1,000:** N/A (No savings)")
        
        with col3:
            st.write(f"**Expense per $1 earned:** ${(expenses/income):.2f}")
