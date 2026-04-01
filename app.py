import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuração da página Web
st.set_page_config(page_title="Torneio AOE II", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_do_sheets():
    # Lê as 3 abas que você criou
    df_civs = conn.read(worksheet="Civs")
    df_ida = conn.read(worksheet="Ida")
    df_volta = conn.read(worksheet="Volta")
    
    # Reconstrói o dicionário 'dados' para o seu código antigo não quebrar
    dados = {
        "civs": {row["Jogador"]: row["Civilizacao"] for _, row in df_civs.iterrows()},
        "ida": df_ida.to_dict('records'),
        "volta": df_volta.to_dict('records')
    }
    return dados

def salvar_no_sheets():
    # Converte o dicionário de volta para tabelas e envia ao Google
    df_civs = pd.DataFrame([{"Jogador": k, "Civilizacao": v} for k, v in st.session_state.dados["civs"].items()])
    df_ida = pd.DataFrame(st.session_state.dados["ida"])
    df_volta = pd.DataFrame(st.session_state.dados["volta"])
    
    conn.update(worksheet="Civs", data=df_civs)
    conn.update(worksheet="Ida", data=df_ida)
    conn.update(worksheet="Volta", data=df_volta)

# Inicialização
if 'dados' not in st.session_state:
    try:
        st.session_state.dados = carregar_do_sheets()
    except:
        # Se a planilha estiver vazia no começo, ele cria o padrão
        st.session_state.dados = {
            "civs": {player: "Pendente" for player in ALL_PLAYERS},
            "ida": [{"t1": "Pendente", "t2": "Pendente", "vencedor": "Nenhum"} for _ in range(6)],
            "volta": [{"t1": "Pendente", "t2": "Pendente", "vencedor": "Nenhum"} for _ in range(6)]
        }
