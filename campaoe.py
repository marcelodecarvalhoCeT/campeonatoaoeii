import tkinter as tk
from tkinter import ttk
import json
import os

class TorneioAOE2App:
    def __init__(self, root):
        self.root = root
        self.root.title("Torneio AOE II - Pontos Corridos")
        self.root.geometry("1000x750")
        
        # Nome do arquivo onde os dados serão salvos
        self.arquivo_save = "save_torneio.json"
        
        # Dados das Duplas
        self.teams_info = {
            "Dupla A": "André + Pedro",
            "Dupla B": "Ariel + Teo",
            "Dupla C": "Tales + Vicente",
            "Dupla D": "Marcelo + Nilo"
        }
        self.team_names = list(self.teams_info.keys())
        
        # Lista de Civilizações
        self.civs = ["Pendente", "Armênios", "Astecas", "Bengalis", "Bizantinos", "Boêmios", "Bretões", 
                     "Búlgaros", "Borgonheses", "Birmaneses", "Celtas", "Chineses", "Cumanos", 
                     "Dravidianos", "Espanhóis", "Etiopes", "Francos", "Georgianos", "Godos", 
                     "Gurjaras", "Hindustanis", "Hunos", "Incas", "Italianos", "Japoneses", 
                     "Khmer", "Coreanos", "Lituanos", "Magiares", "Maias", "Malaios", "Malis", 
                     "Mongóis", "Persas", "Poloneses", "Portugueses", "Romanos", "Sarracenos", 
                     "Sicilianos", "Eslavos", "Tártaros", "Teutões", "Turcos", "Vietnamitas", "Vikings"]
        
        self.team_civs = {team: tk.StringVar(value="Pendente") for team in self.team_names}
        
        # Variáveis dinâmicas para as partidas
        self.partidas_ida = self.criar_lista_partidas(6)
        self.partidas_volta = self.criar_lista_partidas(6)
        
        self.create_widgets()
        self.carregar_estado() # Carrega os dados salvos antes de gerar a tabela
        self.atualizar_classificacao()

    def criar_lista_partidas(self, quantidade):
        return [{"t1": tk.StringVar(value="Pendente"), 
                 "t2": tk.StringVar(value="Pendente"), 
                 "vencedor": tk.StringVar(value="Nenhum"),
                 "cb_vencedor": None} for _ in range(quantidade)]

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        tab_principal = ttk.Frame(notebook)
        tab_regras = ttk.Frame(notebook)
        
        notebook.add(tab_principal, text="Tabela e Jogos")
        notebook.add(tab_regras, text="Configurações e Regras")
        
        self.setup_tab_principal(tab_principal)
        self.setup_tab_regras(tab_regras)

    def setup_tab_principal(self, frame):
        # --- SEÇÃO: SELEÇÃO DE CIVILIZAÇÕES ---
        frame_civs = ttk.LabelFrame(frame, text="🏛️ Seleção de Civilizações Ocultas", padding=10)
        frame_civs.pack(fill='x', padx=10, pady=(10, 5))
        
        for team in self.team_names:
            ttk.Label(frame_civs, text=f"{team}:").pack(side='left', padx=(15, 2))
            cb_civ = ttk.Combobox(frame_civs, textvariable=self.team_civs[team], values=self.civs, state="readonly", width=12)
            cb_civ.pack(side='left', padx=(0, 15))
            cb_civ.bind("<<ComboboxSelected>>", lambda e: self.atualizar_classificacao())

        # --- SEÇÃO: TABELA DE CLASSIFICAÇÃO ---
        frame_tabela = ttk.LabelFrame(frame, text="🏆 Tabela de Classificação", padding=10)
        frame_tabela.pack(fill='x', padx=10, pady=5)
        
        colunas = ("pos", "dupla", "jogadores", "civ", "pontos", "vitorias", "derrotas", "jogos")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=4)
        
        cabecalhos = ["Pos", "Dupla", "Jogadores", "Civilização", "Pontos", "Vitórias", "Derrotas", "Partidas"]
        larguras = [40, 70, 160, 100, 60, 60, 60, 60]
        
        for col, cab, larg in zip(colunas, cabecalhos, larguras):
            self.tree.heading(col, text=cab)
            self.tree.column(col, width=larg, anchor="center")
            
        self.tree.pack(fill='x')
        
        # --- SEÇÃO: JOGOS (IDA E VOLTA) ---
        frame_jogos = ttk.Frame(frame)
        frame_jogos.pack(fill='both', expand=True, padx=10, pady=5)
        
        frame_ida = self.criar_painel_jogos(frame_jogos, self.partidas_ida, "⚔️ First Season (Ida) - Mapa: Arabia")
        frame_ida.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        frame_volta = self.criar_painel_jogos(frame_jogos, self.partidas_volta, "🛡️ Revanche (Volta) - Mapa: Derrotado Decide")
        frame_volta.pack(side='right', fill='both', expand=True, padx=(5, 0))

    def criar_painel_jogos(self, parent_frame, partidas_list, titulo):
        frame = ttk.LabelFrame(parent_frame, text=titulo, padding=10)
        
        ttk.Label(frame, text="Equipe 1", font=('', 9, 'bold')).grid(row=0, column=0, padx=5, pady=(0, 10))
        ttk.Label(frame, text="Equipe 2", font=('', 9, 'bold')).grid(row=0, column=2, padx=5, pady=(0, 10))
        ttk.Label(frame, text="Vencedor", font=('', 9, 'bold')).grid(row=0, column=4, padx=5, pady=(0, 10))

        for i, p_dict in enumerate(partidas_list):
            row_idx = i + 1
            
            cb_t1 = ttk.Combobox(frame, textvariable=p_dict["t1"], values=["Pendente"] + self.team_names, state="readonly", width=10)
            cb_t1.grid(row=row_idx, column=0, padx=5, pady=5)
            
            ttk.Label(frame, text=" X ").grid(row=row_idx, column=1)
            
            cb_t2 = ttk.Combobox(frame, textvariable=p_dict["t2"], values=["Pendente"] + self.team_names, state="readonly", width=10)
            cb_t2.grid(row=row_idx, column=2, padx=5, pady=5)
            
            ttk.Label(frame, text=" -> ").grid(row=row_idx, column=3)
            
            cb_venc = ttk.Combobox(frame, textvariable=p_dict["vencedor"], values=["Nenhum"], state="readonly", width=10)
            cb_venc.grid(row=row_idx, column=4, padx=5, pady=5)
            p_dict["cb_vencedor"] = cb_venc
            
            def update_winner_options(event=None, p=p_dict):
                t1 = p["t1"].get()
                t2 = p["t2"].get()
                opcoes = ["Nenhum"]
                if t1 != "Pendente": opcoes.append(t1)
                if t2 != "Pendente": opcoes.append(t2)
                
                p["cb_vencedor"]['values'] = opcoes
                
                if p["vencedor"].get() not in opcoes:
                    p["vencedor"].set("Nenhum")
                self.atualizar_classificacao()

            cb_t1.bind("<<ComboboxSelected>>", update_winner_options)
            cb_t2.bind("<<ComboboxSelected>>", update_winner_options)
            cb_venc.bind("<<ComboboxSelected>>", lambda e: self.atualizar_classificacao())
            
        return frame

    def setup_tab_regras(self, frame):
        regras_texto = """
        ⚙️ CONFIGURAÇÕES GERAIS DO TORNEIO ⚙️
        
        * Modo: Random Map
        * Mapas: Arabia, Floresta Negra, Mediterrâneo, etc...
        * Velocidade do jogo: Normal (1.7x)
        * Recursos iniciais: Standard
        * Era inicial: Dark Age
        * População máxima: 200
        * Vitória: Conquest 
        * Exploração: Normal 
        * Equipes travadas: Sim 
        * Equipes Juntas: Sim
        * Civilização: Fixa, mas secreta até o dia da primeira partida.
        
        SISTEMA DE PONTOS:
        * Vitória: 3 Pontos
        * Derrota: 0 Pontos
        """
        lbl_regras = ttk.Label(frame, text=regras_texto, font=("Helvetica", 11), justify="left")
        lbl_regras.pack(padx=20, pady=20, anchor="w")

    def atualizar_classificacao(self):
        stats = {k: {"nome": k, "jogadores": self.teams_info[k], "civ": self.team_civs[k].get(), 
                     "pts": 0, "v": 0, "d": 0, "j": 0} for k in self.team_names}
        
        for partida in self.partidas_ida + self.partidas_volta:
            t1 = partida["t1"].get()
            t2 = partida["t2"].get()
            vencedor = partida["vencedor"].get()
            
            if vencedor != "Nenhum" and t1 != "Pendente" and t2 != "Pendente":
                perdedor = t2 if vencedor == t1 else (t1 if vencedor == t2 else None)
                
                if perdedor:
                    stats[vencedor]["pts"] += 3
                    stats[vencedor]["v"] += 1
                    stats[vencedor]["j"] += 1
                    
                    stats[perdedor]["d"] += 1
                    stats[perdedor]["j"] += 1
            
        ranking = list(stats.values())
        ranking.sort(key=lambda x: (x["pts"], x["v"]), reverse=True)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for i, eq in enumerate(ranking):
            valores = (f"{i+1}º", eq['nome'], eq['jogadores'], eq['civ'], 
                       eq['pts'], eq['v'], eq['d'], eq['j'])
            self.tree.insert("", "end", values=valores)
            
        # Salva o estado automaticamente sempre que a classificação é atualizada
        self.salvar_estado()

    def salvar_estado(self):
        dados = {
            "civs": {team: self.team_civs[team].get() for team in self.team_names},
            "ida": [{"t1": p["t1"].get(), "t2": p["t2"].get(), "vencedor": p["vencedor"].get()} for p in self.partidas_ida],
            "volta": [{"t1": p["t1"].get(), "t2": p["t2"].get(), "vencedor": p["vencedor"].get()} for p in self.partidas_volta]
        }
        try:
            with open(self.arquivo_save, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def carregar_estado(self):
        if not os.path.exists(self.arquivo_save):
            return
            
        try:
            with open(self.arquivo_save, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
            # Restaurar civilizações
            for team, civ in dados.get("civs", {}).items():
                if team in self.team_civs:
                    self.team_civs[team].set(civ)
                    
            # Função para restaurar as partidas nos comboboxes
            def restaurar_partidas(lista_partidas, dados_salvos):
                for i, p_data in enumerate(dados_salvos):
                    if i < len(lista_partidas):
                        p = lista_partidas[i]
                        p["t1"].set(p_data["t1"])
                        p["t2"].set(p_data["t2"])
                        
                        # Atualiza as opções dinâmicas do vencedor baseado no save
                        opcoes = ["Nenhum"]
                        if p_data["t1"] != "Pendente": opcoes.append(p_data["t1"])
                        if p_data["t2"] != "Pendente": opcoes.append(p_data["t2"])
                        if p["cb_vencedor"]:
                            p["cb_vencedor"]['values'] = opcoes
                            
                        p["vencedor"].set(p_data["vencedor"])

            restaurar_partidas(self.partidas_ida, dados.get("ida", []))
            restaurar_partidas(self.partidas_volta, dados.get("volta", []))
            
        except Exception as e:
            print(f"Erro ao carregar o save: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    app = TorneioAOE2App(root)
    root.mainloop()