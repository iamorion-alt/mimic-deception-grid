import os, json
import pandas as pd
import streamlit as st

LOG = "/logs/events.jsonl"
st.title("Mimic Deception Grid")

if os.path.exists(LOG):
    rows = []
    with open(LOG) as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

    df = pd.DataFrame(rows)
    st.metric("Total events", len(df))
    st.dataframe(df.tail(100))

    if "source" in df.columns:
        st.bar_chart(df["source"].value_counts())
else:
    st.write("No events yet.")
