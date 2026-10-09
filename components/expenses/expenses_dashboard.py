
import streamlit as st
import matplotlib.pyplot as plt

@st.fragment
def show_expenses_dashboard(spese_dashboard_df):

    st.subheader("💰 Totale spese")

    # Calculate each person's total expenses
    expenses_by_person = (
        spese_dashboard_df.groupby("Nome")["Importo"]
        .sum()
        .sort_values(ascending=False)
    )

    # Display one metric column per person
    if expenses_by_person.empty:
        st.info("Nessuna spesa disponibile.")
    else:
        columns = st.columns(len(expenses_by_person))

        for col, (person, total) in zip(columns, expenses_by_person.items()):
            with col:
                st.metric(
                    label=f"💰 {person}",
                    value=f"{total:,.2f} zł",
            )

    # Expenses dataframe
    st.subheader("Dati")

    st.dataframe(
        spese_dashboard_df[
            [
                "Nome",
                "Importo",
                "Commenti",
            ]
        ],
        width="stretch",
        hide_index=True,
    )