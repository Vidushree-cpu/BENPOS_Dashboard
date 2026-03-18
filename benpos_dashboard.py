import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("BENPOS Interactive Dashboard")

# -------------------------------
# Upload Files
# -------------------------------
st.sidebar.header("Upload Files")

file_current = st.sidebar.file_uploader("Upload Current Week BENPOS", type=["xlsx"])
file_previous = st.sidebar.file_uploader("Upload Previous Week BENPOS (Optional)", type=["xlsx"])

# -------------------------------
# Category Mapping
# -------------------------------
def map_type(category):
    if category in ["AIF", "MF", "FPI", "FPC", "INS", "QIB", "TRU"]:
        return "Institutional"
    elif category in ["PRO", "PRG"]:
        return "Promoter"
    elif category in ["HUF", "LTD", "NRI", "NRN", "PUB"]:
        return "Retail"
    else:
        return "Others"

def map_holding(percent):
    if percent < 1:
        return "<1%"
    elif percent <= 5:
        return "1-5%"
    else:
        return ">5%"

# -------------------------------
# Load & Process
# -------------------------------
def process_file(file):
    df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    # Ensure numeric
    df["Percent"] = pd.to_numeric(df["Percent"], errors="coerce")
    df["Shares"] = pd.to_numeric(df["Shares"], errors="coerce")

    # Type mapping
    df["Type"] = df["Category"].apply(map_type)

    # Holding bucket
    df["Holding Bucket"] = df["Percent"].apply(map_holding)

    return df

if file_current:
    df = process_file(file_current)

    # -------------------------------
    # Free Float Calculation
    # -------------------------------
    promoter_shares = df[df["Type"] == "Promoter"]["Shares"].sum()
    total_shares = df["Shares"].sum()
    free_float = total_shares - promoter_shares

    st.metric("Free Float Shares", f"{free_float:,.0f}")

    # -------------------------------
    # Filters
    # -------------------------------
    st.sidebar.header("Filters")

    type_filter = st.sidebar.multiselect(
        "Select Type",
        options=df["Type"].unique(),
        default=df["Type"].unique()
    )

    holding_filter = st.sidebar.multiselect(
        "Select Holding Bucket",
        options=df["Holding Bucket"].unique(),
        default=df["Holding Bucket"].unique()
    )

    df_filtered = df[
        (df["Type"].isin(type_filter)) &
        (df["Holding Bucket"].isin(holding_filter))
    ]

    # -------------------------------
    # % Holding by Category
    # -------------------------------
    st.subheader("% Holding by Type")

    holding_summary = df_filtered.groupby("Type")["Percent"].sum().reset_index()

    fig = px.pie(holding_summary, values="Percent", names="Type")
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Top Shareholders
    # -------------------------------
    st.subheader("Top Shareholders")

    top_n = st.selectbox("Select Top N", [20, 50])

    top_shareholders = df_filtered.sort_values(by="Percent", ascending=False).head(top_n)

    st.dataframe(top_shareholders[["Name", "Shares", "Percent", "Type"]], use_container_width=True)

    # -------------------------------
    # Top 10 Institutional Investors
    # -------------------------------
    st.subheader("Top 10 Institutional Investors")

    inst_df = df_filtered[df_filtered["Type"] == "Institutional"]

    top_inst = inst_df.sort_values(by="Percent", ascending=False).head(10)

    st.dataframe(top_inst[["Name", "Shares", "Percent"]], use_container_width=True)

    # -------------------------------
    # Week-on-Week Change
    # -------------------------------
    if file_previous:
        st.subheader("Week-on-Week Change")

        df_prev = process_file(file_previous)

        merged = pd.merge(
            df,
            df_prev,
            on="PAN",
            how="outer",
            suffixes=("_current", "_previous")
        )

        merged["Percent_current"] = merged["Percent_current"].fillna(0)
        merged["Percent_previous"] = merged["Percent_previous"].fillna(0)

        merged["Change"] = merged["Percent_current"] - merged["Percent_previous"]

        change_df = merged.sort_values(by="Change", ascending=False)

        st.dataframe(
            change_df[["Name_current", "Percent_previous", "Percent_current", "Change"]].head(20),
            use_container_width=True
        )
