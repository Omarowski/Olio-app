import requests
import streamlit as st


@st.cache_data(ttl=3600)
def get_eur_pln_rate():
    url = "https://api.nbp.pl/api/exchangerates/rates/A/EUR/?format=json"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    rate = data["rates"][0]["mid"]
    rate_date = data["rates"][0]["effectiveDate"]

    return rate, rate_date
