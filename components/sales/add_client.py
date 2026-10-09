
import streamlit as st
import pandas as pd

from config import PRICE_PER_UNIT
from services.google_sheets import save_data


@st.fragment
def show_add_client(worksheet, original_df):

    st.subheader("Aggiungi un nuovo cliente")

    # 1. Create unique keys for each worksheet
    prefix = str(worksheet.id)

    quantity_key = f"new_client_quantity_{prefix}"
    name_key = f"new_client_name_{prefix}"
    phone_key = f"new_client_phone_{prefix}"

    success_key = f"client_saved_{prefix}"
    reset_key = f"reset_client_form_{prefix}"

    # 2. Reset fields BEFORE creating the widgets
    if st.session_state.get(reset_key, False):
        st.session_state[name_key] = ""
        st.session_state[phone_key] = ""
        st.session_state[quantity_key] = 0

        st.session_state[reset_key] = False

    # 3. Display the previous success message
    saved_client = st.session_state.get(success_key)

    if saved_client:
        st.success(
            f"Cliente {saved_client} aggiunto con successo!"
        )

    # 4. Input fields
    new_quantity = st.number_input(
        "Quantità",
        min_value=0,
        step=1,
        key=quantity_key,
    )

    # 5. Calculate the amount automatically
    new_amount = new_quantity * PRICE_PER_UNIT

    st.metric(
        "Importo",
        f"{new_amount:,.0f} zł",
    )

    new_name = st.text_input(
        "Nome",
        key=name_key,
    )

    new_phone = st.text_input(
        "Numero di telefono",
        key=phone_key,
    )

    # 6. Save the client when the button is clicked
    if st.button(
        "Aggiungi cliente",
        type="primary",
        use_container_width=True,
        key=f"add_client_{prefix}",
    ):

        # Validate the name
        if not new_name.strip():
            st.error("Il nome è obbligatorio.")
            return

        # Validate the quantity
        if new_quantity <= 0:
            st.error(
                "La quantità deve essere maggiore di zero."
            )
            return

        try:
            # 7. Create a new row with all existing columns
            new_row = {
                column: ""
                for column in original_df.columns
            }

            new_row["Nome"] = new_name.strip()
            new_row["Quantita'"] = new_quantity
            new_row["Importo"] = f"{new_amount:.0f} zł"
            new_row["NUMERO DI TELEFONO"] = new_phone.strip()

            # 8. Append the new client to the existing data
            updated_df = pd.concat(
                [
                    original_df,
                    pd.DataFrame([new_row]),
                ],
                ignore_index=True,
            )

            # 9. Save the updated data to Google Sheets
            save_data(worksheet, updated_df)

            # 10. Store the success message
            st.session_state[success_key] = new_name.strip()

            # 11. Schedule the fields to reset on the next run
            st.session_state[reset_key] = True

            # 12. Rerun the app
            st.rerun()

        except Exception as error:
            st.error(
                "Errore durante l'aggiunta del cliente."
            )
            st.exception(error)
