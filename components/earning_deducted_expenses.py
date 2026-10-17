import streamlit as st


def show_financial_summary(
    spese_dashboard_df,
    venduto_dashboard_df,
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
    prezzo_macina_raw = spese_dashboard_df.iloc[0, 6]  # Assuming the price is in cell G2

    try:
        prezzo_macina = float(
            prezzo_macina_raw.strip().replace(",", ".")
        )
    except (ValueError, AttributeError):
        prezzo_macina = 0.0

    spese_macina_df = spese_dashboard_df[
    spese_dashboard_df["Commenti"]
    .astype(str)
    .str.strip()
    .str.lower() == "macina"
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
                f"{prezzo_macina:,.2f} EUR"
                if prezzo_macina is not None
                else "N/D"
            ),
        )           

    with col4:
        st.metric(
            label=f"🫒 Totale venduto Confermati",
            value=f"{totale_venduto:,.2f} zł",
        )

    with col5:
        st.metric(
            label="💰 Ricavi netti",
            value=f"{ricavi_netti:,.2f} zł",
        )