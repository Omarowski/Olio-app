
import streamlit as st
import matplotlib.pyplot as plt


@st.fragment
def show_sales_dashboard(dashboard_df, spreadsheet, stato):

    # Filter by customer name
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
        key="sales_names",
    )

    filtered_df = dashboard_df[
        dashboard_df["Nome"].astype(str).isin(selected_names)
    ].copy()

    # Apply the shared status selection
    if stato == "Confermati":
        status_df = filtered_df[
            filtered_df["Confermato"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "yes"
        ].copy()

    elif stato == "Non confermati":
        status_df = filtered_df[
            filtered_df["Confermato"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "no"
        ].copy()

    else:
        status_df = filtered_df.copy()

    st.subheader("Dati")

    st.dataframe(
        status_df[
            ["Nome", "Quantita'", "Importo", "Pagato"]
        ],
        width="stretch",
        hide_index=True,
    )

    quantity = status_df["Quantita'"].sum()
    number_of_customers = status_df["Nome"].nunique()
    amount = status_df["Importo_num"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Prezzo per unità",
            f"{get_price(spreadsheet):,.2f} zł",
        )

    with col2:
        st.metric(
            f"Quantità ({stato.lower()})",
            f"{quantity:g}",
        )

    with col3:
        st.metric(
            f"Numero di clienti ({stato.lower()})",
            f"{number_of_customers}",
        )

    with col4:
        st.metric(
            f"Importo ({stato.lower()})",
            f"{amount:,.2f} zł",
        )

    # Graph based on the same filtered dataframe
    st.subheader("Quantità venduta per nome")

    chart_df = (
        status_df
        .groupby("Nome", as_index=False)["Quantita'"]
        .sum()
        .sort_values("Quantita'", ascending=False)
    )

    if chart_df.empty:
        st.info("Nessun dato disponibile per i filtri selezionati.")
    else:
        fig, ax = plt.subplots(figsize=(12, 8))

        ax.bar(
            chart_df["Nome"],
            chart_df["Quantita'"],
        )

        ax.set_ylim(bottom=0)
        ax.set_xlabel("Nome")
        ax.set_ylabel("Quantità")
        ax.tick_params(axis="x", rotation=90)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


def get_price(spreadsheet):
    price_sheet = spreadsheet.worksheet("Prezzo")
    price_value = price_sheet.acell("A2").value

    return float(price_value)
