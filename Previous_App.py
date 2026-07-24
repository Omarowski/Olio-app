# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import matplotlib.pyplot as plt

# olio_csv = pd.read_csv("Olio - Olio Da Vendere 24_25.csv")

# df = pd.DataFrame(olio_csv)
# df = df.dropna(subset=["Nome"])
# st.title("Olio Venduto 24_25")
# st.sidebar.header("Filtri")
# st.sidebar.subheader("Seleziona i valori per filtrare i dati")

# Nome = st.sidebar.multiselect(
#     "Nome",
#     options=df["Nome"].unique(),
#     default=df["Nome"].unique()
# )
# # Nome = st.sidebar.selectbox("Seleziona un Nome", options=df["Nome"].unique())
# # Filter the dataframe
# filtered_df = df[df["Nome"].isin(Nome)]
# filtered_df.columns = df.columns.str.strip()
# # Display the filtered dataframe
# st.dataframe(filtered_df[['Nome', "Quantita'",'Importo','NUMERO DI TELEFONO']], width='stretch')  

# st.subheader("Grafico a barre della quantità venduta per Nome")

# chart = (
#     df.groupby("Nome", as_index=False)["Quantita'"]
#     .sum()
# )

# fig, ax = plt.subplots(figsize=(12, 8))
# ax.bar(chart["Nome"], chart["Quantita'"])
# ax.set_ylim(bottom=0)
# plt.xticks(rotation=90)

# st.pyplot(fig)

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1vtMaTt1ujTEjPNrfHhMOm4VS1D8FJP5dpT3mrjVaqRI"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes,
)

client = gspread.authorize(creds)

sheet = client.open_by_key(SPREADSHEET_ID).sheet1

df = pd.DataFrame(sheet.get_all_records())

st.write(df)