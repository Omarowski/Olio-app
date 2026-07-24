import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "1vtMaTt1ujTEjPNrfHhMOm4VS1D8FJP5dpT3mrjVaqRI"


@st.cache_resource
def get_worksheet():
    """Connect to the first worksheet in the Google spreadsheet."""

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # gid=0 normally corresponds to the first worksheet.
    return spreadsheet.get_worksheet(0)


def load_data(worksheet):
    """Load the Google Sheet into a Pandas DataFrame."""

    values = worksheet.get_all_values()

    if not values:
        return pd.DataFrame()

    headers = values[0]
    rows = values[1:]

    dataframe = pd.DataFrame(rows, columns=headers)
    dataframe.columns = dataframe.columns.str.strip()

    return dataframe


def save_data(worksheet, dataframe):
    """Replace the worksheet contents with the edited data."""

    clean_df = dataframe.copy()
    clean_df = clean_df.fillna("")

    # Convert NumPy/Pandas values into normal Python strings/numbers.
    values = [
        clean_df.columns.tolist(),
        *clean_df.astype(str).values.tolist(),
    ]

    worksheet.clear()
    worksheet.update(values=values, range_name="A1")


# Connect and load
try:
    worksheet = get_worksheet()
    df = load_data(worksheet)

except Exception as error:
    st.error("Impossibile collegarsi al Google Sheet.")
    st.exception(error)
    st.stop()


if df.empty:
    st.warning("Il Google Sheet è vuoto.")
    st.stop()


required_columns = [
    "Nome",
    "Quantita'",
    "Importo",
    "NUMERO DI TELEFONO",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Nel Google Sheet mancano queste colonne: "
        + ", ".join(missing_columns)
    )

    st.write("Colonne trovate:", df.columns.tolist())
    st.stop()


# Clean the data
df["Nome"] = df["Nome"].astype(str).str.strip()

df = df[df["Nome"] != ""]

df["Quantita'"] = pd.to_numeric(
    df["Quantita'"],
    errors="coerce",
).fillna(0)


# Page
st.title("Olio Venduto 24_25")

dashboard_tab, edit_tab = st.tabs(
    ["Dashboard", "Modifica dati"]
)


with dashboard_tab:
    st.sidebar.header("Filtri")

    st.sidebar.subheader(
        "Seleziona i valori per filtrare i dati"
    )

    names = sorted(df["Nome"].unique())

    selected_names = st.sidebar.multiselect(
        "Nome",
        options=names,
        default=names,
    )

    filtered_df = df[
        df["Nome"].isin(selected_names)
    ]

    st.dataframe(
        filtered_df[
            [
                "Nome",
                "Quantita'",
                "Importo",
                "NUMERO DI TELEFONO",
            ]
        ],
        width="stretch",
        hide_index=True,
    )

    st.subheader(
        "Grafico a barre della quantità venduta per Nome"
    )

    chart = (
        filtered_df
        .groupby("Nome", as_index=False)["Quantita'"]
        .sum()
        .sort_values("Quantita'", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.bar(
        chart["Nome"],
        chart["Quantita'"],
    )

    ax.set_ylim(bottom=0)
    ax.set_xlabel("Nome")
    ax.set_ylabel("Quantità")
    ax.tick_params(axis="x", rotation=90)

    fig.tight_layout()

    st.pyplot(fig)


with edit_tab:
    st.subheader("Modifica il Google Sheet")

    edited_df = st.data_editor(
        df.reset_index(drop=True),
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
    )

    if st.button(
        "Salva modifiche",
        type="primary",
    ):
        try:
            save_data(worksheet, edited_df)

            st.success(
                "Le modifiche sono state salvate nel Google Sheet."
            )

            st.rerun()

        except Exception as error:
            st.error(
                "Errore durante il salvataggio."
            )

            st.exception(error)