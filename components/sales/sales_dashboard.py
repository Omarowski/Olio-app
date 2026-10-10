import streamlit as st
import matplotlib.pyplot as plt


@st.fragment
def show_sales_dashboard(dashboard_df, spreadsheet, stato):

    # ==========================================
    # FILTER BY CUSTOMER NAME
    # ==========================================

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

    # ==========================================
    # FILTER BY ORDER STATUS
    # ==========================================

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

    # ==========================================
    # SALES TABLE
    # ==========================================

    st.subheader("Dati")

    st.dataframe(
        status_df[
            ["Nome", "Quantita'", "Importo", "Pagato"]
        ],
        width="stretch",
        hide_index=True,
    )

    # ==========================================
    # METRICS
    # ==========================================

    quantity = status_df["Quantita'"].sum()
    number_of_customers = status_df["Nome"].nunique()
    amount = status_df["Importo_num"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        price = get_price(spreadsheet)

        st.metric(
            "Prezzo per unità",
            f"{price:,.2f} zł",
        )

        if st.button(
            "✏️ Modifica prezzo",
            key="edit_unit_price",
            help="Modifica il prezzo per unità nel foglio Google Sheets",
        ):
            st.session_state["show_price_editor"] = (
                not st.session_state.get("show_price_editor", False)
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

    # ==========================================
    # EDIT UNIT PRICE
    # ==========================================

    if st.session_state.get("show_price_editor", False):

        st.divider()
        st.subheader("✏️ Modifica prezzo per unità")

        with st.form("unit_price_form"):

            new_price = st.number_input(
                "Nuovo prezzo per unità (zł)",
                min_value=0.0,
                value=float(price),
                step=0.50,
                format="%.2f",
            )

            save_price = st.form_submit_button(
                "💾 Salva prezzo",
                type="primary",
            )

        if save_price:
            try:
                if new_price <= 0:
                    st.error("Il prezzo deve essere maggiore di zero.")

                else:
                    price_sheet = spreadsheet.worksheet("Prezzo")

                    # Update the existing price cell in Google Sheets
                    price_sheet.update_acell("A2", new_price)

                    st.session_state["show_price_editor"] = False

                    st.success(
                        f"Prezzo aggiornato a {new_price:.2f} zł per unità."
                    )

                    st.rerun()

            except Exception as error:
                st.error("Impossibile aggiornare il prezzo su Google Sheets.")
                st.exception(error)

    # ==========================================
    # SALES CHART
    # ==========================================

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


# ==========================================
# GET UNIT PRICE FROM GOOGLE SHEETS
# ==========================================

def get_price(spreadsheet):
    price_sheet = spreadsheet.worksheet("Prezzo")
    price_value = price_sheet.acell("A2").value

    return float(price_value)