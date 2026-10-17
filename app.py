import streamlit as st

from components.earning_deducted_expenses import show_financial_summary
from components.expenses.add_expenses import show_add_expenses
from components.expenses.expenses_dashboard import show_expenses_dashboard
from components.expenses.expenses_editor import show_expenses_editor
from components.payments.show_payments import show_payments_dashboard
from components.status_filter import get_stato

from config import SALES_REQUIRED_COLUMNS, EXPENSE_REQUIRED_COLUMNS

from services.google_sheets import get_spreadsheet, load_data

from utils.data import (
    prepare_expenses_data,
    validate_columns,
    prepare_sales_data,
)

from components.sales.sales_dashboard import show_sales_dashboard
from components.sales.sales_editor import show_sales_editor
from components.sales.add_client import show_add_client


st.set_page_config(
    page_title="🫒 Olio App",
    page_icon="🫒",
    layout="wide",
)


# ==========================================
# PAGE HEADER
# ==========================================

st.title("🫒 Olio App")
st.caption("Gestione vendite, spese e ricavi.")


# ==========================================
# GOOGLE SHEETS CONNECTION
# ==========================================

try:
    spreadsheet = get_spreadsheet()

except Exception as error:
    st.error("Impossibile collegarsi al Google Sheet.")
    st.exception(error)
    st.stop()


# ==========================================
# MAIN PAGE: SALES SHEET SELECTOR
# ==========================================

venduto_sheets = [
    ws.title
    for ws in spreadsheet.worksheets()
    if ws.title.lower().startswith("venduto_")
]

if not venduto_sheets:
    st.error("Nessun foglio Venduto trovato.")
    st.stop()


# Sort sheet names in reverse order, assuming dates use YYYY-MM-DD.
venduto_sheets = sorted(venduto_sheets, reverse=True)

st.subheader("📅 Periodo di riferimento")

selected_venduto = st.selectbox(
    "Seleziona il periodo di vendita",
    venduto_sheets,
    key="selected_venduto",
)

# Find the corresponding expenses worksheet by matching the suffix.
date_suffix = selected_venduto[len("Venduto_"):]

spese_sheets = {
    ws.title.lower(): ws.title
    for ws in spreadsheet.worksheets()
    if ws.title.lower().startswith("spese_")
}

selected_spese = spese_sheets.get(
    f"spese_{date_suffix}".lower()
)

st.divider()


# ==========================================
# LOAD SALES DATA
# ==========================================

try:
    venduto_worksheet = spreadsheet.worksheet(selected_venduto)
    original_df = load_data(venduto_worksheet)

except Exception as error:
    st.error("Impossibile caricare il foglio Venduto.")
    st.exception(error)
    st.stop()


if original_df.empty:
    st.warning("Il foglio Venduto è vuoto.")
    st.stop()


missing_columns = validate_columns(
    original_df,
    SALES_REQUIRED_COLUMNS,
)

if missing_columns:
    st.error(
        "Colonne mancanti nel foglio Venduto: "
        + ", ".join(missing_columns)
    )
    st.stop()


venduto_dashboard_df = prepare_sales_data(original_df)


# ==========================================
# SALES DASHBOARD
# ==========================================
year = venduto_worksheet.title.split("_")[-1]

st.header(f"🫒 Vendite {year}")

stato = get_stato()

dashboard_tab, edit_tab, add_tab = st.tabs(
    [
        "📊 Venduto Dashboard",
        "✏️ Modifica dati",
        "➕ Aggiungi cliente",
    ]
)

with dashboard_tab:
    show_sales_dashboard(
        venduto_dashboard_df,
        spreadsheet,
        stato,
    )

with edit_tab:
    show_sales_editor(
        venduto_worksheet,
        original_df,
        SALES_REQUIRED_COLUMNS,
    )

with add_tab:
    show_add_client(
        venduto_worksheet,
        # original_df,
    )


# ==========================================
# LOAD MATCHING EXPENSE DATA
# ==========================================

st.divider()
st.header(f"💸 Spese {year}")

if not selected_spese:
    st.error(
        f"Non è stato trovato un foglio Spese corrispondente a "
        f"'{selected_venduto}'. "
        f"Assicurati che esista un foglio Spese con lo stesso suffisso."
    )
    st.stop()


try:
    worksheet_spese = spreadsheet.worksheet(selected_spese)
    spese_df = load_data(worksheet_spese)

except Exception as error:
    st.error(
        f"Impossibile caricare il foglio '{selected_spese}'."
    )
    st.exception(error)
    st.stop()


if spese_df.empty:
    st.warning(f"Il foglio '{selected_spese}' è vuoto.")

missing_columns = validate_columns(
    spese_df,
    EXPENSE_REQUIRED_COLUMNS,
)

if missing_columns:
    st.error(
        "Colonne mancanti nel foglio Spese: "
        + ", ".join(missing_columns)
    )
    st.stop()


spese_dashboard_df = prepare_expenses_data(spese_df)


# ==========================================
# EXPENSE DASHBOARD
# ==========================================

spese_dashboard_tab, edit_spese_tab, add_spese_tab = st.tabs(
    [
        "📊 Spese Dashboard",
        "✏️ Modifica spese",
        "➕ Aggiungi spese",
    ]
)

with spese_dashboard_tab:
    show_expenses_dashboard(spese_dashboard_df)

with edit_spese_tab:
    show_expenses_editor(
        worksheet_spese,
        spese_df,
        EXPENSE_REQUIRED_COLUMNS,
    )

with add_spese_tab:
    show_add_expenses(
        worksheet_spese,
        spese_df,
    )


# ==========================================
# FINANCIAL SUMMARY
# ==========================================

st.divider()
st.header("💰 Ricavi al netto delle spese")

show_financial_summary(
    spese_dashboard_df,
    venduto_dashboard_df,
    worksheet_spese
)


# ==========================================
# PAYMENTS
# ==========================================

st.divider()
st.header("💳 Pagamenti ricevuti")

show_payments_dashboard(venduto_dashboard_df)
