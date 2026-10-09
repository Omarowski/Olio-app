import streamlit as st
import gspread

from services.google_sheets import save_data
from utils.data import validate_columns

@st.fragment
def show_sales_editor(
    worksheet,
    original_df,
    required_columns,
):

    st.subheader(
        "Modifica il Google Sheet"
    )

    st.info(
        "Modifica i valori nella tabella e premi "
        "“Salva modifiche”."
    )

    edited_df = st.data_editor(
        original_df.copy(),
        num_rows="dynamic",
        width="stretch",
        hide_index=True,

        # Important when changing worksheets
        key=f"sales_editor_{worksheet.id}",

        column_config={
            "Nome": st.column_config.TextColumn(
                "Nome",
                required=True,
            ),
            "Quantita'": st.column_config.TextColumn(
                "Quantità",
            ),
            "Importo": st.column_config.TextColumn(
                "Importo",
            ),
            "NUMERO DI TELEFONO":
                st.column_config.TextColumn(
                    "Numero di telefono",
                ),
        },
    )

    save_col, cancel_col = st.columns(2)

    with save_col:
        save_clicked = st.button(
            "Salva modifiche",
            type="primary",
            use_container_width=True,
            key=f"save_sales_{worksheet.id}",
        )

    with cancel_col:
        reload_clicked = st.button(
            "Annulla e ricarica",
            use_container_width=True,
            key=f"reload_sales_{worksheet.id}",
        )

    if reload_clicked:
        st.rerun()

    if save_clicked:
        missing = validate_columns(
            edited_df,
            required_columns,
        )

        if missing:
            st.error(
                "Non puoi eliminare queste colonne: "
                + ", ".join(missing)
            )
            return

        try:
            with st.spinner(
                "Salvataggio..."
            ):
                save_data(
                    worksheet,
                    edited_df,
                )

            st.success(
                "Modifiche salvate."
            )

            st.rerun()

        except gspread.exceptions.APIError as error:
            st.error(
                "Google Sheets ha rifiutato "
                "il salvataggio."
            )
            st.exception(error)

        except Exception as error:
            st.error(
                "Errore durante il salvataggio."
            )
            st.exception(error)