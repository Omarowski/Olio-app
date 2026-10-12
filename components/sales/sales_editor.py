import streamlit as st
import gspread

from utils.data import validate_columns


@st.fragment
def show_sales_editor(
    worksheet,
    original_df,
    required_columns,
):

    st.subheader("Modifica il Google Sheet")

    st.info(
        "Modifica i valori nella tabella e premi "
        "“Salva modifiche”. La colonna Importo è "
        "sola lettura perché contiene una formula."
    )

    edited_df = st.data_editor(
        original_df.copy(),
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        key=f"sales_editor_{worksheet.id}",
        disabled=["Importo"],
        column_config={
            "Nome": st.column_config.TextColumn(
                "Nome",
                required=True,
            ),
            "Quantita'": st.column_config.NumberColumn(
                "Quantità",
                min_value=0,
                step=1,
            ),
            "Importo": st.column_config.TextColumn(
                "Importo",
            ),
            "NUMERO DI TELEFONO": st.column_config.TextColumn(
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
            with st.spinner("Salvataggio..."):

                # Read the actual Google Sheets headers
                headers = [
                    str(header).strip()
                    for header in worksheet.row_values(1)
                ]

                # Never write to the Importo column
                writable_columns = [
                    col for col in headers
                    if col.strip().lower() != "importo"
                ]

                # Match edited data to the existing sheet columns
                missing_columns = [
                    col for col in writable_columns
                    if col not in edited_df.columns
                ]

                if missing_columns:
                    st.error(
                        "Mancano queste colonne nel modulo: "
                        + ", ".join(missing_columns)
                    )
                    return

                # Write each editable column separately.
                # This preserves the Importo formula column.
                for column in writable_columns:
                    col_index = headers.index(column) + 1
                    col_letter = gspread.utils.rowcol_to_a1(
                        1, col_index
                    )
                    col_letter = "".join(
                        char for char in col_letter
                        if char.isalpha()
                    )

                    values = [
                        [column],
                        *[
                            ["" if value is None else value]
                            for value in edited_df[column].tolist()
                        ],
                    ]

                    worksheet.update(
                        range_name=f"{col_letter}1:{col_letter}{len(values)}",
                        values=values,
                        value_input_option="USER_ENTERED",
                    )

            st.success("Modifiche salvate.")
            st.rerun()

        except gspread.exceptions.APIError as error:
            st.error(
                "Google Sheets ha rifiutato il salvataggio."
            )
            st.exception(error)

        except Exception as error:
            st.error("Errore durante il salvataggio.")
            st.exception(error)