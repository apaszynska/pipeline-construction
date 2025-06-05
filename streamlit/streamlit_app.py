import streamlit as st
import psycopg
import pandas as pd
# from dotenv import load_dotenv
# import os

# load_dotenv()
st.markdown(
    """
    <style>
    /* Remove or reduce Streamlit main block margins/padding */
    .css-18e3th9 {
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100% !important;
    }
    /* Optionally, remove padding around the entire page */
    .css-1d391kg {
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api_data():
    try:
        dbconn = st.secrets["DB_CONN"]
        with psycopg.connect(dbconn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM api_data;")
                data = cur.fetchall()
        df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])

        df['date'] = pd.to_datetime(df['date']) # Convert 'date' column to datetime type
        df_2025 = df[df['date'].dt.year == 2025]
        df_2025['date'] = df_2025['date'].dt.date
        df_2025.set_index('date', inplace=True)
        df_2025 = df_2025.sort_index(ascending=False)             # Sort dataframe by date ascending
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

if "page" not in st.session_state: # default homepage
    st.session_state.page = "home"

# Sidebar with clickable text (like a nav menu)
with st.sidebar:
    if st.button("🏠 Home"):
        st.session_state.page = "home"
    if st.button("📰 News"):
        st.session_state.page = "news"
    if st.button("📊 Bitcoin Market Data"):
        st.session_state.page = "data"

# Main page content
if st.session_state.page == "home":
    st.markdown('<h1 style="color:#FFA500;">Welcome to Bitcoin Hub</h1>', unsafe_allow_html=True)
    st.write("Stay informed with the latest Bitcoin news, real-time price updates, and expert insights—all in one place.")
    # Create two columns for widgets
    col1, col2 = st.columns(2)
    with col1:
        st.header("📊 Bitcoin Today")
        if not api_data.empty:
            latest = api_data.iloc[0]  # Latest row (assuming sorted descending)
            st.write(f"**Date:** {latest.name}")  # index is date
            st.write(f"**Open:** ${latest['open']}")
            st.write(f"**High:** ${latest['high']}")
            st.write(f"**Low:** ${latest['low']}")
            st.write(f"**Close:** ${latest['close']}")
            st.write(f"**Volume:** {latest['volume']}")
        else:
            st.write("No Bitcoin price data for today available.")

    with col2:
        st.header("🗞️ Latest News")
        if not scraped_data.empty:
            for date, row in scraped_data.head(2).iterrows():
                st.markdown(f"#### {row['title']}")
                st.write(f"*{date.date()}*")
                st.markdown("---")
        else:
            st.write("No articles available.")

elif st.session_state.page == "news":
    st.markdown('<h1 style="color:#FFA500;">📰 News</h1>', unsafe_allow_html=True)
    df_articles = get_scraped_data()
    st.dataframe(df_articles, use_container_width=True)

elif st.session_state.page == "data":
    st.markdown('<h1 style="color:#FFA500;">📊 Bitcoin Market Data</h1>', unsafe_allow_html=True)
    df_data = get_api_data()
    st.dataframe(df_data, use_container_width=True)
    st.line_chart(df_data)