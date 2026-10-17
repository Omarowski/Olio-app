
import streamlit as st
import pandas as pd

from services.google_sheets import save_data
from utils.exchange_rate import get_eur_pln_rate


@st.fragment
def show_add_expenses(worksheet, original_df):
    prefix = str(worksheet.id)

    # Session state keys
    amount_key = f"new_expense_amount_{prefix}"
    name_key = f"new_expense_name_{prefix}"
    comment_key = f"new_comment_{prefix}"
    currency_key = f"new_expense_currency_{prefix}"

    kg_key = f"new_expense_kg_{prefix}"
    litri_key = f"new_expense_litri_{prefix}"

    success_key = f"expenses_saved_{prefix}"
    reset_key = f"reset_expenses_form_{prefix}"

    # Reset fields before creating widgets
    if st.session_state.get(reset_key, False):
        st.session_state[name_key] = "Omar"
        st.session_state[comment_key] = ""
        st.session_state[amount_key] = ""
        st.session_state[currency_key] = "PLN"
        st.session_state[kg_key] = ""
        st.session_state[litri_key] = ""
        st.session_state[reset_key] = False

    st.subheader("Aggiungi una nuova spesa")

    # Get EUR/PLN exchange rate
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

    # Expense details
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

    # Kg and Litri inputs

    col_kg, col_litri, col_resa = st.columns(3)

    with col_kg:
        new_kg = st.text_input(
            "Kg",
            placeholder="Inserisci Kg",
            key=kg_key,
        )

    with col_litri:
        new_litri = st.text_input(
            "Litri",
            placeholder="Inserisci Litri",
            key=litri_key,
        )

    # Calculate Resa safely
    resa_amount = None
    kg_value = None
    litri_value = None

    try:
        kg_text = str(new_kg).strip().replace(",", ".")
        litri_text = str(new_litri).strip().replace(",", ".")

        if kg_text and litri_text:
            kg_value = float(kg_text)
            litri_value = float(litri_text)

            if kg_value >= 0 and litri_value > 0:
                resa_amount = (litri_value/kg_value ) * 100

    except ValueError:
        pass

    with col_resa:
        if resa_amount is not None:
            st.metric("Resa", f"{resa_amount:.4f}")
        else:
            st.metric("Resa", "—")
            st.caption("Inserisci Kg e Litri validi (Litri > 0).")

    new_comment = st.text_input(
        "Commento",
        key=comment_key,
    )

    # Parse the expense amount
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
            st.warning(
                "Inserisci un importo valido, ad esempio 12,50."
            )

    # Show amount in PLN
    if amount_to_save is not None:
        st.metric(
            "Importo da salvare",
            f"{amount_to_save:,.2f} zł",
        )
    elif currency == "EUR" and rate is None:
        st.info(
            "Il cambio non è disponibile; "
            "la conversione EUR → PLN è sospesa."
        )

    # Save expense
    if st.button(
        "Aggiungi spesa",
        type="primary",
        use_container_width=True,
        key=f"add_expense_{prefix}",
    ):
        if not new_amount_text.strip():
            st.error("L'importo è obbligatorio.")


        try:
            entered_amount = float(
                new_amount_text.strip().replace(",", ".")
            )
        except ValueError:
            st.error(
                "Inserisci un importo valido, ad esempio 12,50."
            )


        if entered_amount <= 0:
            st.error("L'importo deve essere maggiore di zero.")


        # Validate Kg and Litri
        try:
            kg_text = str(new_kg).strip().replace(",", ".")
            litri_text = str(new_litri).strip().replace(",", ".")

            if not kg_text or not litri_text:
                st.error("Inserisci sia Kg che Litri.")


            kg_value = float(kg_text)
            litri_value = float(litri_text)

            if kg_value < 0 or litri_value <= 0:
                st.error("Kg deve essere >= 0 e Litri deve essere > 0.")


        except ValueError:
            st.error("Inserisci valori numerici validi per Kg e Litri.")


        # Validate exchange rate at save time
        if currency == "EUR":
            try:
                rate, rate_date = get_eur_pln_rate()
            except Exception:
                st.error(
                    "Impossibile recuperare il cambio. Riprova più tardi."
                )

            amount_to_save = entered_amount * rate
        else:
            amount_to_save = entered_amount

        # Calculate Resa using validated numeric values
        resa_amount = (litri_value / kg_value ) * 100

        try:
            updated_df = original_df.copy()

            required_columns = [
                "Nome",
                "Importo",
                "Commenti",
                "Litri",
                "Kg",
                "Resa",
            ]

            for column in required_columns:
                if column not in updated_df.columns:
                    updated_df[column] = ""

            new_row = {column: "" for column in updated_df.columns}

            new_row["Nome"] = new_name
            new_row["Importo"] = f"{amount_to_save:.2f} zł"
            new_row["Commenti"] = new_comment.strip()
            new_row["Litri"] = litri_value
            new_row["Kg"] = kg_value
            new_row["Resa"] = round(resa_amount, 2)

            updated_df = pd.concat(
                [updated_df, pd.DataFrame([new_row])],
                ignore_index=True,
            )

            save_data(worksheet, updated_df)

            st.session_state[success_key] = new_name
            st.session_state[reset_key] = True

            st.success("Spesa aggiunta correttamente!")
            st.rerun()

        except Exception as error:
            st.error("Errore durante l'aggiunta della spesa.")
            st.exception(error)
