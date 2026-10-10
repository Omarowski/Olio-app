import streamlit as st

from components.sales.sales_dashboard import get_price


@st.fragment
def show_add_client(worksheet, original_df):

    st.subheader("Aggiungi un nuovo cliente")

    # Get the current unit price from Google Sheets
    try:
        spreadsheet = worksheet.spreadsheet
        price_per_unit = get_price(spreadsheet)
    except Exception as error:
        st.error("Impossibile recuperare il prezzo unitario.")
        st.exception(error)
        return

    # Unique keys for each worksheet
    prefix = str(worksheet.id)

    quantity_key = f"new_client_quantity_{prefix}"
    name_key = f"new_client_name_{prefix}"
    phone_key = f"new_client_phone_{prefix}"

    success_key = f"client_saved_{prefix}"
    reset_key = f"reset_client_form_{prefix}"

    # Reset fields before creating widgets
    if st.session_state.get(reset_key, False):
        st.session_state[name_key] = ""
        st.session_state[phone_key] = ""
        st.session_state[quantity_key] = 0
        st.session_state[reset_key] = False

    # Display success message
    saved_client = st.session_state.get(success_key)

    if saved_client:
        st.success(f"Cliente {saved_client} aggiunto con successo!")

    # Input quantity
    new_quantity = st.number_input(
        "Quantità",
        min_value=0,
        step=1,
        key=quantity_key,
    )

    # Calculate amount for display
    new_amount = new_quantity * price_per_unit

    st.metric("Importo", f"{new_amount:,.2f} zł")

    # Input client details
    new_name = st.text_input("Nome", key=name_key)
    new_phone = st.text_input("Numero di telefono", key=phone_key)

    # Add client
    if st.button(
        "Aggiungi cliente",
        type="primary",
        use_container_width=True,
        key=f"add_client_{prefix}",
    ):

        if not new_name.strip():
            st.error("Il nome è obbligatorio.")
            return

        if new_quantity <= 0:
            st.error("La quantità deve essere maggiore di zero.")
            return

        try:
            # Match the existing worksheet column order
            headers = [
                str(header).strip()
                for header in worksheet.row_values(1)
            ]

            # Build the new row in exactly that order
            new_row = {
                "Nome": new_name.strip(),
                "Quantita'": new_quantity,
                "NUMERO DI TELEFONO": new_phone.strip(),
            }

            # Leave Importo blank so the sheet formula calculates it
            row_values = [
                new_row.get(header, "")
                for header in headers
            ]

            # Append only the new row; do not clear or rewrite the sheet
            worksheet.append_row(
                row_values,
                value_input_option="USER_ENTERED",
                insert_data_option="INSERT_ROWS",
            )

            st.session_state[success_key] = new_name.strip()
            st.session_state[reset_key] = True

            st.rerun()

        except Exception as error:
            st.error("Errore durante l'aggiunta del cliente.")
            st.exception(error)