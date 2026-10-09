import streamlit as st


def get_stato():
    return st.selectbox(
        "Stato ordine",
        ["Tutti Gli ordini", "Confermati", "Non confermati"],
        key="sales_status",
    )