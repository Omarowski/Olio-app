import streamlit as st

@st.fragment
def show_payments_dashboard(dashboard_df):

    st.subheader("Pagamenti ricevuti")

    # Filter only paid orders
    paid_df = dashboard_df[
        dashboard_df["Pagato"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
    ].copy()

    # Calculate total paid using the numeric column
    total_paid = paid_df["Importo_num"].sum()

    st.metric(
        "Totale pagato",
        f"{total_paid:,.2f} zł",
    )
    if paid_df.empty:
        st.info("Nessun pagamento ricevuto.")
        return

    # Show only the requested columns
    st.dataframe(
        paid_df[["Nome", "Quantita'", "Importo","Pagato"]],
        width="stretch",
        hide_index=True,
    )


