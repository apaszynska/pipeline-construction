import streamlit as st
import psycopg
import pandas as pd
# from dotenv import load_dotenv
# import os

# load_dotenv()


def get_api_data():
    try:
        dbconn = st.secrets["DB_CONN"]
        with psycopg.connect(dbconn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM api_data;")
                data = cur.fetchall()
        df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['date'])  # Convert 'date' column to datetime type
        df_2025 = df[df['date'].dt.year == 2025]
        df_2025 = df_2025.sort_values('date', ascending=False).reset_index(drop=True)               # Sort dataframe by date ascending
        print(f"Fetched {len(df)} rows, date range {df['date'].min()} to {df['date'].max()}")
        return df_2025
    except Exception as e:
        st.error(f"Error fetching API data: {e}")
        print(f"Error fetching API data: {e}")
        return pd.DataFrame()

def get_scraped_data():
    try:
        dbconn = st.secrets["DB_CONN"]
        with psycopg.connect(dbconn) as conn:   #Using with psycopg.connect(dbconn) as conn: opens the connection
                                                #and automatically closes it when the block ends, even if an error happens inside the block.
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM articles;")
                data = cur.fetchall()
        df = pd.DataFrame(data, columns=['date', 'title'])
        df['date'] = pd.to_datetime(df['date'])  # convert 'date' column to datetime
        df.set_index('date', inplace=True)
        df = df.sort_index(ascending = False)  # sort by date index
        print(f"Fetched {len(df)} articles, date range {df.index.min()} to {df.index.max()}")
        return df
    except Exception as e:
        st.error(f"Error fetching scraped data: {e}")
        print(f"Error fetching scraped data: {e}")
        return pd.DataFrame()

api_data = get_api_data()
scraped_data = get_scraped_data()


col1, col2 = st.columns([4, 8])  # 2/4 left, 3/4 right spacing

with col1:
    st.markdown("<h4 style='color: #1E90FF; marigin: 0; padding: 0;'>Explore:</h4>", unsafe_allow_html=True)
    select_box = st.selectbox("",["Bitcoin Market Prices", "Bitcoin News"])

if select_box == "Bitcoin Market Prices":
    bitcoin = get_api_data()
    st.markdown("<h1 style='color: #FF6347;'>Bitcoin Market Prices 2025</h1>", unsafe_allow_html=True)
    st.dataframe(bitcoin)
    st.line_chart(bitcoin.set_index('date')[['open', 'close']])
elif select_box == "Bitcoin News":
    articles = get_scraped_data()
    st.markdown("<h1 style='color: #FF6347;'>Bitcoin News</h1>", unsafe_allow_html=True)
    st.dataframe(articles)