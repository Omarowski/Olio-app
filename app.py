import streamlit as st

from components.earning_deducted_expenses import show_financial_summary
from components.expenses.add_expenses import show_add_expenses
from components.expenses.expenses_dashboard import show_expenses_dashboard
from components.expenses.expenses_editor import show_expenses_editor
from components.payments.show_payments import show_payments_dashboard
from components.status_filter import get_stato
from config import SALES_REQUIRED_COLUMNS, EXPENSE_REQUIRED_COLUMNS

from services.google_sheets import (
    get_spreadsheet,
    load_data,
)

from utils.data import (
    prepare_expenses_data,
    validate_columns,
    prepare_sales_data,
)

from components.sales.sales_dashboard import (
    show_sales_dashboard,
)

from components.sales.sales_editor import (
    show_sales_editor,
)

from components.sales.add_client import (
    show_add_client,
)


st.set_page_config(
    page_title="🫒 Olio App",
    page_icon="🫒",
    layout="wide",
)


# ==========================================
# GOOGLE SHEETS VENDUTO
# ==========================================

try:
    spreadsheet = get_spreadsheet()

    venduto_sheets = [
        ws.title
        for ws in spreadsheet.worksheets()
        if "venduto" in ws.title.lower()
    ]

    selected_venduto = st.sidebar.selectbox(
        "🫒 Foglio Venduto",
        venduto_sheets,
    )

    venduto_worksheet = spreadsheet.worksheet(
        selected_venduto
    )

    original_df = load_data(
        venduto_worksheet
    )

except Exception as error:
    st.error(
        "Impossibile collegarsi "
        "al Google Sheet."
    )
    st.exception(error)
    st.stop()


# ==========================================
# VALIDATION
# ==========================================

if original_df.empty:
    st.warning(
        "Il Google Sheet è vuoto."
    )
    st.stop()


missing_columns = validate_columns(
    original_df,
    SALES_REQUIRED_COLUMNS,
)

if missing_columns:
    st.error(
        "Colonne mancanti: "
        + ", ".join(missing_columns)
    )
    st.stop()


venduto_dashboard_df = prepare_sales_data(
    original_df
)


# ==========================================
# TITLE
# ==========================================

st.title(f"🫒 {venduto_worksheet.title}")

# ==========================================
# TABS
# ==========================================
stato = get_stato()
dashboard_tab, edit_tab, add_tab = st.tabs(
    [
        "Venduto Dashboard",
        "Modifica dati",
        "Aggiungi cliente",
    ]
)

with dashboard_tab:
    show_sales_dashboard(
        venduto_dashboard_df,
        spreadsheet,
        stato
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
        original_df,
    )

# ==========================================
# GOOGLE SHEETS SPESE
# ==========================================

st.divider()

try:
    spese_spreadsheet = get_spreadsheet()

    spese_sheets = [
        ws.title
        for ws in spese_spreadsheet.worksheets()
        if "spese" in ws.title.lower()
    ]

    st.sidebar.markdown(
    "<div style='height: 50px;'></div>",
    unsafe_allow_html=True,
    )

    selected_spese = st.sidebar.selectbox(
        "🫒 Foglio Spese",
        spese_sheets,
    )

    worksheet_spese = spese_spreadsheet.worksheet(
        selected_spese
    )

    spese_df = load_data(
        worksheet_spese
    )

except Exception as error:
    st.error(
        "Impossibile collegarsi "
        "al Google Sheet."
    )
    st.exception(error)
    st.stop()

# ==========================================
# VALIDATION
# ==========================================

if spese_df.empty:
    st.warning(
        "Il Google Sheet è vuoto."
    )
    # st.stop()


missing_columns = validate_columns(
    spese_df,
    EXPENSE_REQUIRED_COLUMNS,
)

if missing_columns:
    st.error(
        "Colonne mancanti: "
        + ", ".join(missing_columns)
    )
    st.stop()


spese_dashboard_df = prepare_expenses_data(
    spese_df
)

# ==========================================
# TITLE
# ==========================================

st.title(
    f"🫒 {worksheet_spese.title}"
)

# ==========================================
# TABS
# ==========================================

spese_dashboard_tab, edit_spese_tab, add_spese_tab = st.tabs(
    [
        "Spese Dashboard",
        "Modifica spese",
        "Aggiungi Spese",
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

# ===================================
# RICAVI TOLTE LE SPESE
# ===================================

st.title("💰 Ricavi al netto delle spese")

show_financial_summary(
    spese_dashboard_df,
    venduto_dashboard_df,
    stato,
)

show_payments_dashboard(
    venduto_dashboard_df,
)