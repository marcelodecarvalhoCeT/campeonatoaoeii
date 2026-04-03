import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json
import os

# Configuração da página Web
st.set_page_config(page_title="Torneio AOE II", layout="wide")

# 1. VARIÁVEIS DO TORNEIO
PLAYERS_INFO = {
    "Dupla A": ["André", "Pedro"],
    "Dupla B": ["Ariel", "Teo"],
    "Dupla C": ["Tales", "Vicente"],
    "Dupla D": ["Marcelo", "Nilo"]
}
TEAM_NAMES = list(PLAYERS_INFO.keys())
ALL_PLAYERS = [jogador for dupla in PLAYERS_INFO.values() for jogador in dupla]

CIVS = ["Pendente", "Armênios", "Astecas", "Bengalis", "Bizantinos", "Boêmios", "Bretões", 
        "Búlgaros", "Borgonheses", "Birmaneses", "Celtas", "Chineses", "Cumanos", 
        "Dravidianos", "Espanhóis", "Etiopes", "Francos", "Georgianos", "Godos", 
        "Gurjaras", "Hindustanis", "Hunos", "Incas", "Italianos", "Japoneses", 
        "Khmer", "Coreanos", "Lituanos", "Magiares", "Maias", "Malaios", "Malis", 
        "Mongóis", "Persas", "Poloneses", "Portugueses", "Romanos", "Sarracenos", 
        "Sicilianos", "Eslavos", "Tártaros", "Teutões", "Turcos", "Vietnamitas", "Vikings"]

# 2. CONEXÃO COM O GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FUNÇÕES DE DADOS (Com a indentação correta)
def carregar_do_sheets():
    df_civs = conn.read(worksheet="Civs")
    df_ida = conn.read(worksheet="Ida")
    df_volta = conn.read(worksheet="Volta")
    
    # 1. Carrega as civs, mas se a planilha estiver vazia, cria o padrão "Pendente"
    civs_dict = {}
    if getattr(df_civs, 'empty', True) == False and "Jogador" in df_civs.columns:
        civs_dict = {row["Jogador"]: row["Civilizacao"] for _, row in df_civs.iterrows()}
    
    # Garante que todos os jogadores (André, Pedro, Marcelo...) existam na lista
    for player in ALL_PLAYERS:
        if player not in civs_dict:
            civs_dict[player] = "Pendente"
            
    # 2. Carrega as partidas de Ida. Se estiver vazio, cria as 6 partidas padrão
    ida_list = df_ida.to_dict('records') if getattr(df_ida, 'empty', True) == False else []
    if len(ida_list) == 0:
        ida_list = [{"t1": "Pendente", "t2": "Pendente", "vencedor": "Nenhum"} for _ in range(6)]
        
    # 3. Carrega as partidas de Volta. Se estiver vazio, cria as 6 partidas padrão
    volta_list = df_volta.to_dict('records') if getattr(df_volta, 'empty', True) == False else []
    if len(volta_list) == 0:
        volta_list = [{"t1": "Pendente", "t2": "Pendente", "vencedor": "Nenhum"} for _ in range(6)]

    dados = {
        "civs": civs_dict,
        "ida": ida_list,
        "volta": volta_list
    }
    return dados
    
    # --- INICIALIZAÇÃO DA MEMÓRIA ---
if 'dados' not in st.session_state:
    st.session_state.dados = carregar_do_sheets()
    
def salvar_no_sheets():
    # Repare no espaço vazio aqui no começo de cada linha abaixo!
    """Converte o dicionário atual para DataFrames e envia para o Sheets."""
    
    # 1. Prepara e salva as Civilizações
    df_civs = pd.DataFrame(list(st.session_state.dados["civs"].items()), columns=["Jogador", "Civilizacao"])
    conn.update(worksheet="Civs", data=df_civs)
    
    # 2. Prepara e salva as Partidas de Ida
    df_ida = pd.DataFrame(st.session_state.dados["ida"])
    conn.update(worksheet="Ida", data=df_ida)
    
    # 3. Prepara e salva as Partidas de Volta
    df_volta = pd.DataFrame(st.session_state.dados["volta"])
    conn.update(worksheet="Volta", data=df_volta)
    
    # Limpa a memória para o app baixar a versão atualizada
    st.cache_data.clear()
    
with st.sidebar:
    st.markdown("### ☁️ Sincronização")
    # O botão agora chama a sua função correta
    if st.button("💾 Salvar Alterações na Nuvem", use_container_width=True):
        with st.spinner("Enviando para o Google Sheets..."):
            salvar_no_sheets()
            st.success("Tudo salvo com sucesso!")
    
# 4. INICIALIZAÇÃO DO ESTADO
if 'dados' not in st.session_state:
    try:
        st.session_state.dados = carregar_do_sheets()
    except:
        st.session_state.dados = {
            "civs": {player: "Pendente" for player in ALL_PLAYERS},
            "ida": [{"t1": "Pendente", "t2": "Pendente", "vencedor": "Nenhum"} for _ in range(6)],
            "volta": [{"t1": "Pendente", "t2": "Pendente", "vencedor": "Nenhum"} for _ in range(6)]
        }
# --- INTERFACE WEB ---
st.title("🏆 Torneio AOE II - Pontos Corridos")

tab1, tab2 = st.tabs(["Tabela e Jogos", "Configurações e Regras"])

with tab1:
    st.subheader("🏛️ Seleção de Civilizações Ocultas")
    cols = st.columns(4)
    for i, (team, players) in enumerate(PLAYERS_INFO.items()):
        with cols[i]:
            st.markdown(f"**{team}**") # Título da dupla
            for player in players:
                nova_civ = st.selectbox(player, CIVS, index=CIVS.index(st.session_state.dados["civs"][player]), key=f"civ_{player}")
                if nova_civ != st.session_state.dados["civs"][player]:
                    st.session_state.dados["civs"][player] = nova_civ
                    

    st.subheader("🏆 Tabela de Classificação")
    
    # Lógica de Pontuação e Formatação da Tabela
    stats = {}
    for k in TEAM_NAMES:
        j1, j2 = PLAYERS_INFO[k][0], PLAYERS_INFO[k][1]
        civ_texto = f'{st.session_state.dados["civs"][j1]} + {st.session_state.dados["civs"][j2]}'
        
        stats[k] = {
            "Dupla": k, 
            "Jogadores": f"{j1} & {j2}", 
            "Civilizações": civ_texto, 
            "Pontos": 0, "Vitórias": 0, "Derrotas": 0, "Partidas": 0
        }
    
    for fase in ["ida", "volta"]:
        for p in st.session_state.dados[fase]:
            t1, t2, venc = p["t1"], p["t2"], p["vencedor"]
            if venc != "Nenhum" and t1 != "Pendente" and t2 != "Pendente":
                perd = t2 if venc == t1 else (t1 if venc == t2 else None)
                if perd:
                    stats[venc]["Pontos"] += 3
                    stats[venc]["Vitórias"] += 1
                    stats[venc]["Partidas"] += 1
                    stats[perd]["Derrotas"] += 1
                    stats[perd]["Partidas"] += 1

    # Renderiza a Tabela
    df = pd.DataFrame(list(stats.values()))
    df = df.sort_values(by=["Pontos", "Vitórias"], ascending=[False, False]).reset_index(drop=True)
    df.index += 1 
    st.dataframe(df, width='stretch')

    st.divider()

    # Layout dos Confrontos
    col_ida, col_volta = st.columns(2)
    
    def render_fase(fase_key, titulo, col):
        with col:
            st.subheader(titulo)
            
            # --- CABEÇALHO (Aparece só uma vez no topo) ---
            h1, hx1, h2, hx2, h3 = st.columns([4, 1, 4, 1, 4])
            with h3:
                # O markdown com HTML ajuda a centralizar e dar destaque ao título
                st.markdown("<p style='text-align: center; font-weight: bold; margin-bottom: 0px; color: #555;'>VENCEDOR</p>", unsafe_allow_html=True)

            # --- LINHAS DE PARTIDA ---
            for i in range(6):
                p = st.session_state.dados[fase_key][i]
                
                # Criando as 5 colunas (Equipe, X, Equipe, Seta, Vencedor)
                c1, cx1, c2, cx2, c3 = st.columns([4, 1, 4, 1, 4])
                
                with c1:
                    t1 = st.selectbox("Equipe 1", ["Pendente"] + TEAM_NAMES, index=(["Pendente"] + TEAM_NAMES).index(p["t1"]), key=f"{fase_key}_t1_{i}", label_visibility="collapsed")
                
                with cx1:
                    # O margin-top alinha o 'X' com o meio da caixinha
                    st.markdown("<p style='text-align: center; margin-top: 8px;'>✖️</p>", unsafe_allow_html=True)
                
                with c2:
                    t2 = st.selectbox("Equipe 2", ["Pendente"] + TEAM_NAMES, index=(["Pendente"] + TEAM_NAMES).index(p["t2"]), key=f"{fase_key}_t2_{i}", label_visibility="collapsed")
                
                with cx2:
                    # Coloquei uma setinha para indicar o resultado, mas pode trocar por "X" se preferir!
                    st.markdown("<p style='text-align: center; margin-top: 8px;'>➡️</p>", unsafe_allow_html=True)
                
                # Lógica para mostrar apenas os times selecionados como opções de vitória
                opcoes_venc = ["Nenhum"]
                if t1 != "Pendente": opcoes_venc.append(t1)
                if t2 != "Pendente": opcoes_venc.append(t2)
                
                venc_atual = p["vencedor"] if p["vencedor"] in opcoes_venc else "Nenhum"
                
                with c3:
                    venc = st.selectbox("Vencedor", opcoes_venc, index=opcoes_venc.index(venc_atual), key=f"{fase_key}_venc_{i}", label_visibility="collapsed")

                # Se houver qualquer mudança, salva no Sheets
                if t1 != p["t1"] or t2 != p["t2"] or venc != p["vencedor"]:
                    st.session_state.dados[fase_key][i]["t1"] = t1
                    st.session_state.dados[fase_key][i]["t2"] = t2
                    st.session_state.dados[fase_key][i]["vencedor"] = venc
                   
    # --- CHAMADAS DA FUNÇÃO COM OS NOMES NOVOS ---
    render_fase("ida", "⚔️ Primeira Rodada", col_ida)
    render_fase("volta", "🛡️ Revanche", col_volta)
    
with tab2:
    st.markdown("""
    ### ⚙️ CONFIGURAÇÕES GERAIS DO TORNEIO ⚙️
    * **Modo:** Random Map
    * **Mapas:** Arabia, Floresta Negra, Mediterrâneo, etc...
    * **Velocidade do jogo:** Normal (1.7x)
    * **Recursos iniciais:** Standard
    * **Era inicial:** Dark Age
    * **População máxima:** 200
    * **Vitória:** Conquest 
    * **Exploração:** Normal 
    * **Equipes travadas:** Sim 
    * **Equipes Juntas:** Sim
    * **Civilização:** Fixa, secreta até o dia da primeira partida.
    
    ### 📊 SISTEMA DE PONTOS
    * **Vitória:** 3 Pontos
    * **Derrota:** 0 Pontos
    """)
