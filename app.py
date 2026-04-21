import streamlit as st 
import pandas as pd
import plotly.express as px
from database import (create_table, add_expense, get_all_expenses, delete_expense, get_expenses_summary)
from datetime import date
import anthropic
from dotenv import load_dotenv
import os

#Loading environment variables from .env file, per ex: API keys
load_dotenv()

#Configuring the streamlit page, was the first st command
st.set_page_config(
    page_title="FinZ",
    page_icon="💶",
    layout="wide"
)


#Customizing CSS to style metric cards and sidebar
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


#Was ensuring the database exists before any operations
create_table()

#Sidebar navigation
st.sidebar.title("💶 FinZ")
st.sidebar.markdown("---")

#Buttons control for which page it renders, stored in page variable
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Add Expense", "History", "AI Advisor"]
)

#Dashboard Page
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    rows = get_all_expenses()

    if len(rows) == 0:
        st.info("No expenses yet. Go to Add Expense to get started!")
    else:
        #Converts raw database tuples into a Pandas Dataframe for processing
        df = pd.DataFrame(rows, columns=["id", "amount", "category", "description", "date"])
        
        #calculating summary statistics using Pandas
        total_spent = df["amount"].sum()
        top_category = df.groupby("category")["amount"].sum().idxmax()
        total_transactions = len(df)
        
        #Display metric cards in 3 equal columns
        col1, col2, col3 = st.columns(3)
        with col1:
           st.metric("💶 Total Spent", f"€{total_spent:.2f}")
        with col2:
            st.metric("📌 Top Category", top_category)
        with col3:
            st.metric("🧾 Transactions", total_transactions)
        
        #2 Charts side by side
        st.markdown("---")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
          st.subheader("Spending by Category")
          #Group amounts by category for the pie chart
          category_df = df.groupby("category")["amount"].sum().reset_index()
          fig1 = px.pie(category_df, values="amount", names="category", hole=0.4)
          st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
          st.subheader("Expenses Over Time")
          #Group amounts by date for the bar chart
          time_df = df.groupby("date")["amount"].sum().reset_index()
          fig2 = px.bar(time_df, x="date", y="amount", color_discrete_sequence=["#534AB7"])
          st.plotly_chart(fig2, use_container_width=True)

#Add Expense Page
elif page == "Add Expense":
        st.title("➕ Add Expense")
        
        #st.form groups all inputs, nothing is submitted until the button is clicked
        with st.form("expense_form"):
           amount = st.number_input("Amount (€)", min_value=0.01, step=0.01)


           category = st.selectbox("Category", [
            "Food", "Transport", "Housing",
            "Entertainment", "Healthcare", "Other"
           ])

           description = st.text_input("Description", placeholder="e.g. Grocery Shopping")
           
           #default date is today, but the user can change it
           expense_date = st.date_input("Date", value=date.today())

           submitted = st.form_submit_button("Save Expense")

        if submitted:
          #Converts data object to string, SQLite stores dates as Text
          add_expense(amount, category, description, str(expense_date))
          st.success(f"✅ €{amount:.2f} added under {category}!")

#History Page
elif page == "History":
    st.title("History")

    rows = get_all_expenses()

    if len(rows) == 0:
        st.info("No expenses yet")
    else:
        df = pd.DataFrame(rows, columns=["id", "amount", "category", "description", "date"])

        #Format amount column as currency string for display
        df["amount"] = df["amount"].apply(lambda x: f"€{x:.2f}")

        st.dataframe(df, use_container_width=True, hide_index=True)


#A.I Advisory Page
elif page == "AI Advisor":
    st.title("🤖 AI Advisor")
    st.markdown("Ask me anything about your spending habits.")
    
    #Starts with key from environment variables
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    #session_state persists chat history across Streamlit reruns
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    #Render all previous messages in the chat UI
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    user_input = st.chat_input("Ask about finances...")

    if user_input:
        #Save and display the user's message
        st.session_state.messages.append({"role": "user",
                                          "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        #Fetch real spending data to put into the AI prompt
        spending_summary = get_expenses_summary()
        
        #System prompt explains the AI who it is supposed to be and gives it the user's data
        system_prompt = f"""You are a helpful personal finance advisor.
You have access to the user's real spending data:

{spending_summary}

Give specific, actionable advice based on their actual numbers.
Be concise, friendly, and direct. Use euros for amounts."""

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                #Send full conversation history so A.I maintains context
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
                reply = response.content[0].text

                st.write(reply)
        st.session_state.messages.append({"role": "assistant",
                                          "content": reply})