
import streamlit as st
import pandas as pd

from services.google_sheets import save_data
from utils.exchange_rate import get_eur_pln_rate


@st.fragment
def show_add_expenses(worksheet, original_df):
    prefix = str(worksheet.id)

    amount_key = f"new_expense_amount_{prefix}"
    name_key = f"new_expense_name_{prefix}"
    comment_key = f"new_comment_{prefix}"
    currency_key = f"new_expense_currency_{prefix}"

    success_key = f"expenses_saved_{prefix}"
    reset_key = f"reset_expenses_form_{prefix}"

    # Reset fields before creating widgets
    if st.session_state.get(reset_key, False):
        st.session_state[name_key] = ""
        st.session_state[comment_key] = ""
        st.session_state[amount_key] = ""
        st.session_state[currency_key] = "PLN"
        st.session_state[reset_key] = False

    st.subheader("Aggiungi una nuova spesa")

    # Get the latest published EUR/PLN rate
    rate = None
    rate_date = None

    try:
        rate, rate_date = get_eur_pln_rate()
        st.metric(
            "💶 Cambio EUR → PLN",
            f"{rate:.4f} zł",
            delta=f"Cambio al: {rate_date}",
        )
    except Exception:
        st.warning("Impossibile recuperare il cambio EUR/PLN.")

    # # Input fields
    # new_name = st.text_input(
    #     "Nome",
    #     key=name_key,
    # )
    available_names = ["Omar", "Diego"]
    col1, col2, col3 = st.columns(3)

    with col1:
        new_name = st.selectbox(
            "Nome",
            options=available_names,
            key=name_key,
        )
    with col2:
        new_amount_text = st.text_input(
            "Importo",
            key=amount_key,
            placeholder="Es. 12,50",
        )

    with col3:
        currency = st.selectbox(
            "Valuta",
            options=["PLN", "EUR"],
            key=currency_key,
        )

    new_comment = st.text_input(
        "Commento",
        key=comment_key,
    )

    # Parse the entered amount
    amount_to_save = None

    try:
        text = new_amount_text.strip().replace(",", ".")
        entered_amount = float(text) if text else 0.0

        if entered_amount > 0:
            if currency == "EUR":
                if rate is not None:
                    amount_to_save = entered_amount * rate
            else:
                amount_to_save = entered_amount

    except ValueError:
        if new_amount_text.strip():
            st.warning("Inserisci un importo valido, ad esempio 12,50.")

    # Show the amount that will be saved in PLN
    if amount_to_save is not None:
        st.metric("Importo da salvare", f"{amount_to_save:,.2f} zł")
    elif currency == "EUR" and rate is None:
        st.info("Il cambio non è disponibile; la conversione EUR → PLN è sospesa.")

    # Save expense
    if st.button(
        "Aggiungi spesa",
        type="primary",
        use_container_width=True,
        key=f"add_expense_{prefix}",
    ):
        # if not new_name.strip():
        #     st.error("Il nome è obbligatorio.")
        #     return

        if not new_amount_text.strip():
            st.error("L'importo è obbligatorio.")
            return

        try:
            entered_amount = float(
                new_amount_text.strip().replace(",", ".")
            )
        except ValueError:
            st.error("Inserisci un importo valido, ad esempio 12,50.")
            return

        if entered_amount <= 0:
            st.error("L'importo deve essere maggiore di zero.")
            return

        # Recalculate and validate at save time
        if currency == "EUR":
            try:
                rate, rate_date = get_eur_pln_rate()
            except Exception:
                st.error("Impossibile recuperare il cambio. Riprova più tardi.")
                return

            amount_to_save = entered_amount * rate
        else:
            amount_to_save = entered_amount

        try:
            new_row = {column: "" for column in original_df.columns}
            new_row["Nome"] = new_name.strip()
            new_row["Importo"] = f"{amount_to_save:.2f} zł"
            new_row["Commenti"] = new_comment.strip()

            updated_df = pd.concat(
                [original_df, pd.DataFrame([new_row])],
                ignore_index=True,
            )

            save_data(worksheet, updated_df)

            st.session_state[success_key] = new_name.strip()
            st.session_state[reset_key] = True
            st.rerun()

        except Exception as error:
            st.error("Errore durante l'aggiunta della spesa.")
            st.exception(error)
