import pandas as pd


def validate_columns(
    dataframe,
    required_columns,
):
    return [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

# =========================================
# SALES DATA PREPARATION
# =========================================

def prepare_sales_data(dataframe):
    df = dataframe.copy()

    df["Nome"] = (
        df["Nome"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["Nome"] != ""
    ].copy()

    df["Quantita'"] = pd.to_numeric(
        df["Quantita'"]
        .astype(str)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    ).fillna(0)

    df["Importo_num"] = (
        df["Importo"]
        .astype(str)
        .str.replace("zł", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["Importo_num"] = pd.to_numeric(
        df["Importo_num"],
        errors="coerce",
    ).fillna(0)

    return df
# =========================================
# EXPENSES DATA PREPARATION
# =========================================

def prepare_expenses_data(dataframe):
    df = dataframe.copy()

    df["Nome"] = (
        df["Nome"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["Nome"] != ""
    ].copy()

    df["Commenti"] = (
        df["Commenti"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["Commenti"] != ""
    ].copy()

    df["Importo"] = (
        df["Importo"]
        .astype(str)
        .str.replace("zł", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["Importo"] = pd.to_numeric(
        df["Importo"],
        errors="coerce",
    ).fillna(0)

    return df