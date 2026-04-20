import streamlit as st 
import pandas as pd
import plotly.express as px
from database import (create_table, add_expense, get_all_expenses, delete_expense, get_expenses_summary)
from datetime import date
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        [data-testid="stSidebar"] {
            background-color: #1a1a2e;
            }
        [data-testid="stSidebar"] * {
            color: white !important;
            }
        [data-testid="stMetric"] {
            background-color: #1a1a2e;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #534AB7;
            }
        [data-testid="stMetricLabel"] {
            color: #a0a0b0 !important;
            }
        [data-testid="stMetricValue"] {
            color: white !important;}
        [data-testid="column"] {
            padding: 0 8px;}
        </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="FinZ",
    page_icon="💶",
    layout="wide"
)

create_table()

st.sidebar.title("💶 FinZ")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Add Expense", "History", "AI Advisor"]
)

if page == "Dashboard":
    st.title("📊 Dashboard")
    
    rows = get_all_expenses()

    if len(rows) == 0:
        st.info("No expenses yet. Go to Add Expense to get started!")
    else:
        df = pd.DataFrame(rows, columns=["id", "amount", "category", "description", "date"])

        total_spent = df["amount"].sum()
        top_category = df.groupby("category")["amount"].sum().idxmax()
        total_transactions = len(df)

        col1, col2, col3 = st.columns(3)
        with col1:
           st.metric("💶 Total Spent", f"€{total_spent:.2f}")
        with col2:
            st.metric("📌 Top Category", top_category)
        with col3:
            st.metric("🧾 Transactions", total_transactions)

        st.markdown("---")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
          st.subheader("Spending by Category")
          category_df = df.groupby("category")["amount"].sum().reset_index()
          fig1 = px.pie(category_df, values="amount", names="category", hole=0.4)
          st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
          st.subheader("Expenses Over Time")
          time_df = df.groupby("date")["amount"].sum().reset_index()
          fig2 = px.bar(time_df, x="date", y="amount", color_discrete_sequence=["#534AB7"])
          st.plotly_chart(fig2, use_container_width=True)


elif page == "Add Expense":
        st.title("➕ Add Expense")
    
        with st.form("expense_form"):
           amount = st.number_input("Amount (€)", min_value=0.01, step=0.01)


           category = st.selectbox("Category", [
            "Food", "Transport", "Housing",
            "Entertainment", "Healthcare", "Other"
           ])

           description = st.text_input("Description", placeholder="e.g. Grocery Shopping")

           expense_date = st.date_input("Date", value=date.today())

           submitted = st.form_submit_button("Save Expense")

        if submitted:
          add_expense(amount, category, description, str(expense_date))
          st.success(f"✅ €{amount:.2f} added under {category}!")

elif page == "History":
    st.title("History")

    rows = get_all_expenses()

    if len(rows) == 0:
        st.info("No expenses yet")
    else:
        df = pd.DataFrame(rows, columns=["id", "amount", "category", "description", "date"])
        df["amount"] = df["amount"].apply(lambda x: f"€{x:.2f}")

        st.dataframe(df, use_container_width=True, hide_index=True)



elif page == "AI Advisor":
    st.title("🤖 AI Advisor")
    st.markdown("Ask me anything about your spending habits.")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    user_input = st.chat_input("Ask about finances...")

    if user_input:
        st.session_state.messages.append({"role": "user",
                                          "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)

        spending_summary = get_expenses_summary()

        system_prompt = f"""You are a helpful personal finance advisor.
You have access to the user's real spending data:

{spending_summary}

Give specific, actionable advice based on their actual numbers.
Be concise, friendly, and direct. Use euros for amounts."""

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                              *st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content 
                st.write(reply)
        st.session_state.messages.append({"role": "assistant",
                                          "content": reply})