import streamlit as st
import pandas as pd
import gspread

from google.oauth2.service_account import Credentials

from config import SPREADSHEET_ID


@st.cache_resource
def get_spreadsheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes,
    )

    client = gspread.authorize(credentials)

    return client.open_by_key(SPREADSHEET_ID)


def load_data(worksheet):
    values = worksheet.get_all_values()

    if not values:
        return pd.DataFrame()

    headers = [
        str(header).strip()
        for header in values[0]
    ]

    rows = values[1:]
    normalized_rows = []

    for row in rows:
        normalized_row = list(
            row[:len(headers)]
        )

        if len(normalized_row) < len(headers):
            normalized_row.extend(
                [""] * (
                    len(headers)
                    - len(normalized_row)
                )
            )

        normalized_rows.append(
            normalized_row
        )

    return pd.DataFrame(
        normalized_rows,
        columns=headers,
    )


def save_data(worksheet, dataframe):
    clean_df = dataframe.copy()

    clean_df.columns = [
        str(column).strip()
        for column in clean_df.columns
    ]

    clean_df = clean_df.fillna("")

    values = [
        clean_df.columns.tolist(),
        *clean_df.astype(str).values.tolist(),
    ]

    worksheet.clear()

    return worksheet.update(
        range_name="A1",
        values=values,
        value_input_option="USER_ENTERED",
    )