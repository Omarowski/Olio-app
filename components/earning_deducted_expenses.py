import pandas as pd
import streamlit as st


def _parse_number(value):
    """Convert '12,50', '12.50 EUR', 12.5 etc. to float, or None if not possible."""
    if value is None or pd.isna(value):
        return None
    cleaned = (
        str(value)
        .replace("EUR", "")
        .replace("€", "")
        .replace("zł", "")
        .replace("\xa0", "")
        .replace(" ", "")
        .replace(",", ".")
        .strip()
    )
    return pd.to_numeric(cleaned, errors="coerce") if cleaned else None


def show_financial_summary(
    spese_dashboard_df,
    venduto_dashboard_df,
    worksheet_spese
):
    # Filter sales based on the selected status
    filtered_venduto_df = venduto_dashboard_df[
        venduto_dashboard_df["Confermato"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "yes"
    ].copy()

    # Calculate totals
    totale_spese = spese_dashboard_df["Importo"].sum()
    totale_venduto = filtered_venduto_df["Importo_num"].sum()
    ricavi_netti = totale_venduto - totale_spese

    # Price of Macina (cell G2) - safe lookup
    prezzo_macina = worksheet_spese.acell("G2").value

    spese_macina_df = spese_dashboard_df[
        spese_dashboard_df["Commenti"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "macina"
    ]
    # Sum only Macina expenses
    totale_spese_macina = spese_macina_df["Importo"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="💸 Totale spese",
            value=f"{totale_spese:,.2f} zł",
        )
    with col2:
        st.metric(
            label="💸 Totale spese Macina",
            value=f"{totale_spese_macina:,.2f} zł",
        )
    with col3:
        st.metric(
            label="Prezzo Macina",
            value=(
                f"{prezzo_macina} EUR"
            ),
        )
    with col4:
        st.metric(
            label="🫒 Totale venduto Confermati",
            value=f"{totale_venduto:,.2f} zł",
        )
    with col5:
        st.metric(
            label="💰 Ricavi netti",
            value=f"{ricavi_netti:,.2f} zł",
        )