import streamlit as st
import psycopg
import pandas as pd
# from dotenv import load_dotenv
# import os

# load_dotenv()


def get_api_data():
    dbconn = st.secrets["DB_CONN"]
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()

    cur.execute('''
                SELECT * FROM api_data;
                ''')
    data = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return pd.DataFrame(data, columns=['date', 'open','high','low','close', 'volume'])

def get_scraped_data():
    dbconn = st.secrets["DB_CONN"]
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()

    cur.execute('''
                SELECT * FROM articles;
                ''')
    data = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    df = pd.DataFrame(data, columns = ['date','title'])
    df.set_index('date', inplace = True)
    return df

api_data = get_api_data()
scraped_data = get_scraped_data()

st.title("API Data from PostgreSQL")
st.dataframe(api_data)  # Show table
st.line_chart(api_data.set_index('date')[['open', 'close']])  # Plot open and close prices over time

st.title("Scraped Data")
st.dataframe(scraped_data)