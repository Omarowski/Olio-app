import streamlit as st


def show_financial_summary(
    spese_dashboard_df,
    venduto_dashboard_df,
    stato,
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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💸 Totale spese",
            value=f"{totale_spese:,.2f} zł",
        )

    with col2:
        st.metric(
            label=f"🫒 Totale venduto Confermati",
            value=f"{totale_venduto:,.2f} zł",
        )

    with col3:
        st.metric(
            label="💰 Ricavi netti",
            value=f"{ricavi_netti:,.2f} zł",
        )