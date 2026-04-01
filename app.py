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
def salvar_dados():
    with open(ARQUIVO_SAVE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.dados, f, ensure_ascii=False, indent=4)

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
                    salvar_dados()
                    st.rerun()

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
    st.dataframe(df, use_container_width=True)

    st.divider()

    # Layout dos Confrontos
    col_ida, col_volta = st.columns(2)
    
    def render_fase(fase_key, titulo, col):
        with col:
            st.subheader(titulo)
            for i in range(6):
                p = st.session_state.dados[fase_key][i]
                c1, c2, c3 = st.columns([2, 2, 2])
                
                with c1:
                    t1 = st.selectbox("Equipe 1", ["Pendente"] + TEAM_NAMES, index=(["Pendente"] + TEAM_NAMES).index(p["t1"]), key=f"{fase_key}_t1_{i}", label_visibility="collapsed")
                with c2:
                    t2 = st.selectbox("Equipe 2", ["Pendente"] + TEAM_NAMES, index=(["Pendente"] + TEAM_NAMES).index(p["t2"]), key=f"{fase_key}_t2_{i}", label_visibility="collapsed")
                
                opcoes_venc = ["Nenhum"]
                if t1 != "Pendente": opcoes_venc.append(t1)
                if t2 != "Pendente": opcoes_venc.append(t2)
                
                venc_atual = p["vencedor"] if p["vencedor"] in opcoes_venc else "Nenhum"
                
                with c3:
                    venc = st.selectbox("Vencedor", opcoes_venc, index=opcoes_venc.index(venc_atual), key=f"{fase_key}_venc_{i}", label_visibility="collapsed")

                if t1 != p["t1"] or t2 != p["t2"] or venc != p["vencedor"]:
                    st.session_state.dados[fase_key][i]["t1"] = t1
                    st.session_state.dados[fase_key][i]["t2"] = t2
                    st.session_state.dados[fase_key][i]["vencedor"] = venc
                    salvar_dados()
                    st.rerun()

    render_fase("ida", "⚔️ First Season (Arabia)", col_ida)
    render_fase("volta", "🛡️ Revanche (Derrotado Decide)", col_volta)

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
