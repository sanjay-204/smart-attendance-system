import streamlit as st
import pandas as pd
import os

st.title("📊 Attendance Dashboard")

file = "attendance.csv"

if os.path.exists(file):
    df = pd.read_csv(file)

    st.subheader("All Records")
    st.dataframe(df)

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    today_df = df[df["Date"] == today]

    st.subheader("Today's Attendance")
    st.dataframe(today_df)

    st.metric("Present Today", len(today_df))

    st.download_button("Download CSV", df.to_csv(index=False))

else:
    st.warning("No attendance yet")