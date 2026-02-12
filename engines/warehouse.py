def apply_capacity(df, capacity):

    df["Capacity_Breach"] = df["Stock"] > capacity
    df.loc[df["Stock"] > capacity, "Stock"] = capacity

    return df