import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SPREADSHEET_ID = "1vtMaTt1ujTEjPNrfHhMOm4VS1D8FJP5dpT3mrjVaqRI"
# WORKSHEET_ID = 0  

REQUIRED_COLUMNS = [
    "Nome",
    "Quantita'",
    "Importo",
    "NUMERO DI TELEFONO",
]


# ---------------------------------------------------------
# Google Sheets connection
# ---------------------------------------------------------

@st.cache_resource
def get_spreadsheet():
    """
    Connect to the Google spreadsheet and return the worksheet
    whose gid is 0.
    """

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes,
    )

    client = gspread.authorize(credentials)

    # spreadsheet = client.open_by_key(SPREADSHEET_ID)  

    # worksheet = spreadsheet.get_worksheet_by_name(WORKSHEET_ID)
    # worskeet = spredsheet.get_worksheet_by_name("Foglio1")

    # if worksheet is None:
    #     raise ValueError(
    #         f"Non è stato trovato il foglio con ID {WORKSHEET_ID}."
    #     )

    return client.open_by_key(SPREADSHEET_ID)


# ---------------------------------------------------------
# Read and write functions
# ---------------------------------------------------------

def load_data(worksheet):
    """
    Read all values from Google Sheets.

    Values are initially kept as text so phone numbers and other
    formatting-sensitive fields are not changed unintentionally.
    """

    values = worksheet.get_all_values()

    if not values:
        return pd.DataFrame()

    headers = [
        str(header).strip()
        for header in values[0]
    ]

    rows = values[1:]

    # Make every row the same length as the header.
    normalized_rows = []

    for row in rows:
        normalized_row = list(row[:len(headers)])

        if len(normalized_row) < len(headers):
            normalized_row.extend(
                [""] * (len(headers) - len(normalized_row))
            )

        normalized_rows.append(normalized_row)

    dataframe = pd.DataFrame(
        normalized_rows,
        columns=headers,
    )

    return dataframe


def save_data(worksheet, dataframe):
    """
    Replace the worksheet values with the edited DataFrame.
    """

    clean_df = dataframe.copy()

    clean_df.columns = [
        str(column).strip()
        for column in clean_df.columns
    ]

    clean_df = clean_df.fillna("")

    # Convert all values to ordinary strings.
    # This helps preserve phone numbers and avoids NumPy serialization errors.
    values = [
        clean_df.columns.tolist(),
        *clean_df.astype(str).values.tolist(),
    ]

    worksheet.clear()

    result = worksheet.update(
        range_name="A1",
        values=values,
        value_input_option="USER_ENTERED",
    )

    return result


# ---------------------------------------------------------
# Data validation
# ---------------------------------------------------------

def validate_columns(dataframe):
    """
    Return a list of required columns missing from the sheet.
    """

    return [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]


def prepare_dashboard_data(dataframe):
    """
    Create a cleaned copy for filters and charts.

    The original DataFrame remains unchanged for editing and saving.
    """

    dashboard_df = dataframe.copy()

    dashboard_df["Nome"] = (
        dashboard_df["Nome"]
        .astype(str)
        .str.strip()
    )

    dashboard_df = dashboard_df[
        dashboard_df["Nome"] != ""
    ].copy()

    dashboard_df["Quantita'"] = pd.to_numeric(
        dashboard_df["Quantita'"]
        .astype(str)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    ).fillna(0)

    return dashboard_df


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="🫒Olio App",
    page_icon="🫒",
    layout="wide",
)




# ---------------------------------------------------------
# Connect and load data
# ---------------------------------------------------------

try:
    # worksheet = get_worksheet()
    # original_df = load_data(worksheet)
    spreadsheet = get_spreadsheet()

    worksheet_names = [
        ws.title
        for ws in spreadsheet.worksheets()
        if "venduto" in ws.title.lower()
    ]
    # print(worksheet_names)
    selected_sheet = st.sidebar.selectbox(
        "📄 Seleziona la Tab per verificare i dati",
        worksheet_names,
    )

    worksheet = spreadsheet.worksheet(selected_sheet)
    
    original_df = load_data(worksheet)

except Exception as error:
    st.error("Impossibile collegarsi al Google Sheet.")
    st.exception(error)
    st.stop()


if original_df.empty:
    st.warning("Il Google Sheet è vuoto.")
    st.stop()


missing_columns = validate_columns(original_df)

if missing_columns:
    st.error(
        "Nel Google Sheet mancano le seguenti colonne: "
        + ", ".join(missing_columns)
    )

    st.write(
        "Colonne trovate:",
        original_df.columns.tolist(),
    )

    st.stop()


dashboard_df = prepare_dashboard_data(original_df)

splitted_title = [title for title in worksheet.title.split("_")]
result = " & ".join(
    sp_title
    for sp_title in splitted_title
    if sp_title.lower().isnumeric()
)


st.title(f"🫒 Olio Venduto {result}")

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Informazioni")

# st.sidebar.write(
#     f"Foglio collegato: **{worksheet.title}**"
# )

st.sidebar.write(
    f"Nome Worksheet: **{worksheet.title}**"
)

if st.sidebar.button(
    "Ricarica dati dal Google Sheet",
    use_container_width=True,
):
    st.rerun()


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

dashboard_tab, edit_tab, new_client_tab = st.tabs(
    [
        "Dashboard",
        "Modifica dati",
        "Aggiungi cliente"
    ]
)


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

with dashboard_tab:
    st.subheader("Filtri")

    available_names = sorted(
        dashboard_df["Nome"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_names = st.multiselect(
        "Seleziona uno o più nomi",
        options=available_names,
        default=available_names,
    )

    filtered_df = dashboard_df[
        dashboard_df["Nome"].isin(selected_names)
    ].copy()

    st.subheader("Dati")

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
    filtered_df["Importo_num"] = (
        filtered_df["Importo"]
        .astype(str)
        .str.replace("zł", "", regex=False)
        .str.replace(",", "", regex=False)   # remove thousands separator
        .str.strip()
    )

    filtered_df["Importo_num"] = pd.to_numeric(
        filtered_df["Importo_num"],
        errors="coerce",
    ).fillna(0)


    total_amount = filtered_df["Importo_num"].sum()
    total_quantity = filtered_df["Quantita'"].sum()
    number_of_customers = filtered_df["Nome"].nunique()
    

    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    # print(total_amount.dtype)
    with metric_col_1:
        st.metric(
            "Quantità totale",
            f"{total_quantity:g}",
        )

    with metric_col_2:
        st.metric(
            "Numero di clienti",
            number_of_customers,
        )
    with metric_col_3:
        st.metric(
            "Importo totale",
            f"{total_amount:,.0f} zł",
        )
    st.subheader(
        "Quantità venduta per nome"
    )

    chart_df = (
        dashboard_df
        .groupby(
            "Nome",
            as_index=False,
        )["Quantita'"]
        .sum()
        .sort_values(
            "Quantita'",
            ascending=False,
        )
    )


    fig, ax = plt.subplots(
            figsize=(12, 8)
        )

    ax.bar(
            chart_df["Nome"],
            chart_df["Quantita'"],
        )

    ax.set_ylim(bottom=0)
    ax.set_xlabel("Nome")
    ax.set_ylabel("Quantità")
    ax.tick_params(
            axis="x",
            rotation=90,
    )

    fig.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


# ---------------------------------------------------------
# Editing
# ---------------------------------------------------------

with edit_tab:
    st.subheader("Modifica il Google Sheet")

    st.info(
        "Modifica i valori nella tabella e premi "
        "“Salva modifiche”. Le modifiche non vengono "
        "inviate a Google Sheets finché non premi il pulsante."
    )

    edited_df = st.data_editor(
        original_df.copy(),
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        key="olio_data_editor",
        column_config={
            "Nome": st.column_config.TextColumn(
                "Nome",
                required=True,
            ),
            "Quantita'": st.column_config.TextColumn(
                "Quantità",
            ),
            "Importo": st.column_config.TextColumn(
                "Importo",
            ),
            "NUMERO DI TELEFONO": st.column_config.TextColumn(
                "Numero di telefono",
            ),
        },
    )

    save_column, cancel_column = st.columns(2)

    with save_column:
        save_clicked = st.button(
            "Salva modifiche",
            type="primary",
            use_container_width=True,
        )

    with cancel_column:
        reload_clicked = st.button(
            "Annulla e ricarica",
            use_container_width=True,
        )

    if reload_clicked:
        st.rerun()

    if save_clicked:
        try:
            edited_missing_columns = validate_columns(
                edited_df
            )

            if edited_missing_columns:
                st.error(
                    "Non puoi eliminare queste colonne: "
                    + ", ".join(edited_missing_columns)
                )

            else:
                with st.spinner(
                    "Salvataggio nel Google Sheet..."
                ):
                    result = save_data(
                        worksheet,
                        edited_df,
                    )

                updated_cells = (
                    result.get("updatedCells")
                    or result
                    .get("updates", {})
                    .get("updatedCells")
                )

                if updated_cells:
                    st.success(
                        "Modifiche salvate correttamente. "
                        f"Celle aggiornate: {updated_cells}."
                    )
                else:
                    st.success(
                        "Modifiche salvate correttamente "
                        "nel Google Sheet."
                    )

                st.rerun()

        except gspread.exceptions.APIError as error:
            st.error(
                "Google Sheets ha rifiutato il salvataggio. "
                "Controlla che il service account abbia "
                "il permesso Editor."
            )

            st.exception(error)

        except Exception as error:
            st.error(
                "Si è verificato un errore durante "
                "il salvataggio."
            )

            st.exception(error)

PRICE_PER_UNIT = 330

with new_client_tab:
    st.subheader("Aggiungi un nuovo cliente")

    # Show the saved message after rerun
    if "new_client_success" in st.session_state:
        st.success(st.session_state.pop("new_client_success"))

    # Reset fields before widgets are created
    if st.session_state.get("reset_new_client_form", False):
        st.session_state["new_client_quantity"] = 0
        st.session_state["new_client_name"] = ""
        st.session_state["new_client_phone"] = ""
        st.session_state["reset_new_client_form"] = False

    new_quantity = st.number_input(
        "Quantità",
        min_value=0,
        step=1,
        key="new_client_quantity",
    )

    new_amount = new_quantity * PRICE_PER_UNIT

    st.metric(
        "Importo",
        f"{new_amount:,.0f} zł",
    )

    with st.form("new_client_form"):
        new_name = st.text_input(
            "Nome",
            key="new_client_name",
        )

        new_phone = st.text_input(
            "Numero di telefono",
            key="new_client_phone",
        )

        submitted = st.form_submit_button(
            "Aggiungi cliente",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not new_name.strip():
            st.error("Il nome è obbligatorio.")

        elif new_quantity <= 0:
            st.error(
                "La quantità deve essere maggiore di zero."
            )

        else:
            try:
                new_row = {
                    column: ""
                    for column in original_df.columns
                }

                new_row["Nome"] = new_name.strip()
                new_row["Quantita'"] = new_quantity
                new_row["Importo"] = f"{new_amount:.0f} zł"
                new_row["NUMERO DI TELEFONO"] = new_phone.strip()

                updated_df = pd.concat(
                    [
                        original_df,
                        pd.DataFrame([new_row]),
                    ],
                    ignore_index=True,
                )

                save_data(
                    worksheet,
                    updated_df,
                )

                # Store message so it appears after rerun
                st.session_state["new_client_success"] = (
                    f"'{new_name}' e' stato aggiunto "
                    # f"con importo di {new_amount:,.0f} zł."
                )

                st.session_state["reset_new_client_form"] = True

                st.rerun()

            except Exception as error:
                st.error(
                    "Errore durante l'aggiunta del cliente."
                )
                st.exception(error)