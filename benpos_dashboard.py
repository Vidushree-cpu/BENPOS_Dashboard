def process_file(file):
    df = pd.read_excel(file)

    # Clean column names
    df.columns = df.columns.str.strip().str.upper()

    # DEBUG: Show columns in app (remove later)
    st.write("Columns detected:", df.columns)

    # Flexible column mapping
    def find_col(possible_names):
        for col in df.columns:
            for name in possible_names:
                if name in col:
                    return col
        return None

    percent_col = find_col(["PERCENT", "%"])
    shares_col = find_col(["SHARES"])
    category_col = find_col(["CATEGORY"])
    pan_col = find_col(["PAN"])
    name_col = find_col(["NAME"])

    # Rename safely
    df = df.rename(columns={
        percent_col: "Percent",
        shares_col: "Shares",
        category_col: "Category",
        pan_col: "PAN",
        name_col: "Name"
    })

    # Convert numeric
    df["Percent"] = pd.to_numeric(df["Percent"], errors="coerce")
    df["Shares"] = pd.to_numeric(df["Shares"], errors="coerce")

    # Type mapping
    df["Type"] = df["Category"].apply(map_type)

    # Holding bucket
    df["Holding Bucket"] = df["Percent"].apply(map_holding)

    return df
