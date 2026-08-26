# ==============================================================================
# COPYRIGHT (C) 2026 B2 FIlmes
# TODOS OS DIREITOS RESERVADOS.
#
# Autor: Gabriel Menge
# Aplicação: AjaSchedule 1.04 - Control e Agendador AJA KUMO 64x64
# ==============================================================================

import json
import logging
import os
import re
import sys
import threading
import time
import tkinter as tk
import uuid
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
from locales import obter_nome_porta, _
import requests
from PIL import Image, ImageTk

# Importa as estruturas de tradução e o gerenciador I18n
from locales import I18n, LOCALES

# Configuração de diretório de logs
PASTA_LOGS = "logs"
if not os.path.exists(PASTA_LOGS):
    os.makedirs(PASTA_LOGS)

ARQUIVO_LOG = os.path.join(PASTA_LOGS, f"agendador_{datetime.now().strftime('%Y_%m')}.log")

# Configuração base do Logging no arquivo e console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("==================================================")


class GuiLogHandler(logging.Handler):
    """
    Handler customizado de Logging que captura TODAS as mensagens do sistema
    e redireciona para o widget de texto na aba de Logs.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            try:
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
            except Exception:
                pass
        try:
            self.text_widget.after(0, append)
        except Exception:
            pass


# Importações dos módulos locais
try:
    from config import MAP_DIAS_INDEX
except ImportError:
    MAP_DIAS_INDEX = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo",
    }

try:
    from config import ORIGENS_NOMES_DEFAULT, DESTINOS_NOMES_DEFAULT
except ImportError:
    ORIGENS_NOMES_DEFAULT = {i+1: f"Origem {i+1:02d}" for i in range(64)}
    DESTINOS_NOMES_DEFAULT = {i+1: f"Destino {i+1:02d}" for i in range(64)}

try:
    from config import KUMO_IP_DEFAULT
except ImportError:
    try:
        from config import MATRIX_IP
        KUMO_IP_DEFAULT = MATRIX_IP
    except ImportError:
        KUMO_IP_DEFAULT = "192.168.0.2"

try:
    from componentes import HoverButton
except ImportError:
    class HoverButton(tk.Button):
        def __init__(self, master=None, bg_normal=None, bg_hover=None, fg_normal=None, fg_hover=None, **kw):
            super().__init__(master, **kw)
            self.bg_normal = bg_normal or self.cget("bg")
            self.bg_hover = bg_hover or self.bg_normal
            self.fg_normal = fg_normal or self.cget("fg")
            self.fg_hover = fg_hover or self.fg_normal
            self.configure(bg=self.bg_normal, fg=self.fg_normal, activebackground=self.bg_hover, activeforeground=self.fg_hover, bd=0)
            self.bind("<Enter>", lambda e: self.configure(bg=self.bg_hover, fg=self.fg_hover))
            self.bind("<Leave>", lambda e: self.configure(bg=self.bg_normal, fg=self.fg_normal))

try:
    from popups import SeletorCanalPopup, SeletorDiasPopup
except ImportError:
    pass

JSON_AGENDAMENTOS_FILE = "agendamentos.json"
JSON_LABELS_FILE = "labels.json"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def sanitizar_tempo(valor):
    if not valor:
        return "00"
    match = re.search(r"\d+", str(valor))
    if match:
        num = int(match.group())
        return f"{num:02d}"
    return "00"

def aplicar_icone(janela, nome_icone="logo.ico"):
    """
    Aplica o ícone na janela informada tratando o diretório dinâmico do PyInstaller.
    """
    try:
        if hasattr(sys, "_MEIPASS"):
            caminho_abs = os.path.join(sys._MEIPASS, nome_icone)
        else:
            caminho_abs = os.path.abspath(nome_icone)

        if os.path.exists(caminho_abs):
            janela.iconbitmap(caminho_abs)
    except Exception as e:
        logging.warning(f"Não foi possível aplicar o ícone: {e}")

def definir_icone_padrao_global(caminho_icone="logo.ico"):
    """
    Define o ícone padrão para TODAS as janelas (Tk e Toplevel) criadas no aplicativo.
    """
    try:
        if hasattr(sys, '_MEIPASS'):
            caminho_abs = os.path.join(sys._MEIPASS, caminho_icone)
        else:
            caminho_abs = os.path.abspath(caminho_icone)

        if os.path.exists(caminho_abs):
            # Cria uma janela oculta temporária só para aplicar a regra global
            root_temp = tk.Tk()
            root_temp.withdraw()  # Esconde a janela imediatamente

            if caminho_abs.lower().endswith(".ico"):
                # O parâmetro default=True faz TODAS as janelas herdarem o ícone
                root_temp.iconbitmap(default=caminho_abs)
            else:
                img = ImageTk.PhotoImage(Image.open(caminho_abs))
                root_temp.iconphoto(True, img)  # True = aplica globalmente

            root_temp.destroy()  # Destrói a janela temporária
    except Exception as e:
        logging.warning(f"Não foi possível aplicar o ícone global: {e}")

def obter_ou_perguntar_idioma(arquivo_config="config.json"):
    config_data = {}

    if os.path.exists(arquivo_config):
        try:
            with open(arquivo_config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                if "idioma" in config_data and config_data["idioma"] in LOCALES:
                    return config_data["idioma"]
        except Exception:
            pass

    root_lang = tk.Tk()
    root_lang.title("AjaSchedule - Language / Idioma")
    root_lang.geometry("450x190")
    root_lang.configure(bg="#1E1E1E")
    root_lang.resizable(False, False)
    
    # Aplica o ícone e força o foco no topo
    aplicar_icone(root_lang)
    root_lang.attributes("-topmost", True)
    root_lang.lift()
    root_lang.focus_force()

    root_lang.update_idletasks()
    largura, altura = 450, 190
    pos_x = (root_lang.winfo_screenwidth() // 2) - (largura // 2)
    pos_y = (root_lang.winfo_screenheight() // 2) - (altura // 2)
    root_lang.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    idioma_escolhido = ["pt_BR"]

    root_lang.protocol("WM_DELETE_WINDOW", root_lang.destroy)

    tk.Label(
        root_lang,
        text="SELECT SYSTEM LANGUAGE\nSELECIONE O IDIOMA DO SISTEMA",
        font=("Arial", 11, "bold"),
        fg="#00E5FF",
        bg="#1E1E1E",
        pady=15,
    ).pack()

    frame_botoes = tk.Frame(root_lang, bg="#1E1E1E")
    frame_botoes.pack(pady=10)

    def selecionar(lang):
        idioma_escolhido[0] = lang
        config_data["idioma"] = lang
        try:
            with open(arquivo_config, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
        except Exception:
            pass
        root_lang.destroy()

    HoverButton(
        frame_botoes, text="Português", font=("Arial", 9, "bold"),
        bg_normal="#2B2B2B", bg_hover="#3E3E3E", fg_normal="#FFFFFF", fg_hover="#00E5FF",
        padx=10, pady=8, command=lambda: selecionar("pt_BR")
    ).pack(side="left", padx=5)

    HoverButton(
        frame_botoes, text="English", font=("Arial", 9, "bold"),
        bg_normal="#2B2B2B", bg_hover="#3E3E3E", fg_normal="#FFFFFF", fg_hover="#00E5FF",
        padx=10, pady=8, command=lambda: selecionar("en_US")
    ).pack(side="left", padx=5)

    HoverButton(
        frame_botoes, text="Español", font=("Arial", 9, "bold"),
        bg_normal="#2B2B2B", bg_hover="#3E3E3E", fg_normal="#FFFFFF", fg_hover="#00E5FF",
        padx=10, pady=8, command=lambda: selecionar("es_ES")
    ).pack(side="left", padx=5)

    root_lang.mainloop()
    return idioma_escolhido[0]

def obter_ou_perguntar_ip_matriz(arquivo_config="config.json"):
    config_data = {}

    if os.path.exists(arquivo_config):
        try:
            with open(arquivo_config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                if "ip_matriz" in config_data and config_data["ip_matriz"].strip():
                    return config_data["ip_matriz"]
        except Exception:
            pass

    ip_padrao = getattr(sys.modules[__name__], "KUMO_IP_DEFAULT", "192.168.0.2")
    ip_escolhido = [ip_padrao]

    root_ip = tk.Tk()
    root_ip.title(I18n.t("ip_title"))
    root_ip.geometry("450x190")
    root_ip.configure(bg="#1E1E1E")
    root_ip.resizable(False, False)

    # Aplica o ícone e força o foco no topo
    aplicar_icone(root_ip)
    root_ip.attributes("-topmost", True)
    root_ip.lift()
    root_ip.focus_force()

    root_ip.update_idletasks()
    largura, altura = 450, 190
    pos_x = (root_ip.winfo_screenwidth() // 2) - (largura // 2)
    pos_y = (root_ip.winfo_screenheight() // 2) - (altura // 2)
    root_ip.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    root_ip.protocol("WM_DELETE_WINDOW", root_ip.destroy)

    lbl_instrucao = tk.Label(
        root_ip, 
        text=I18n.t("ip_instruction"), 
        fg="#00E5FF", 
        bg="#1E1E1E", 
        font=("Arial", 11, "bold"),
        pady=15
    )
    lbl_instrucao.pack()

    entry_ip = tk.Entry(
        root_ip, 
        font=("Segoe UI", 11), 
        bg="#2B2B2B",
        fg="#00E5FF",
        insertbackground="#FFFFFF",
        bd=0,
        highlightthickness=1,
        highlightbackground="#444444",
        justify="center", 
        width=25
    )
    entry_ip.insert(0, ip_padrao)
    entry_ip.pack(pady=5)
    entry_ip.focus_set()
    entry_ip.select_range(0, tk.END)

    def salvar_ip():
        valor = entry_ip.get().strip()
        if not valor:
            valor = ip_padrao

        ip_escolhido[0] = valor
        config_data["ip_matriz"] = valor

        try:
            with open(arquivo_config, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            logging.error(f"Erro ao salvar IP: {e}")

        root_ip.destroy()

    btn_confirmar = HoverButton(
        root_ip, 
        text=I18n.t("btn_save_continue"), 
        command=salvar_ip, 
        bg_normal="#2B2B2B", 
        bg_hover="#3E3E3E",
        fg_normal="#FFFFFF", 
        fg_hover="#00E5FF",
        font=("Arial", 9, "bold"), 
        padx=12, 
        pady=6
    )
    btn_confirmar.pack(pady=12)

    root_ip.bind("<Return>", lambda event: salvar_ip())
    root_ip.mainloop()

    return ip_escolhido[0]

class AgendadorKumo64x64(tk.Tk):

    def __init__(self, idioma_atual="en_US", ip_matriz=None):
        super().__init__()

        self.id_agendamento_em_edicao = None
        self.arquivo_config = "config.json"

        # Define o idioma ativo recebido da inicialização
        self.idioma_atual = idioma_atual

        # Define o título traduzido
        self.title(self.tr("app_title"))

        try:
            self.state("zoomed")
        except Exception:
            pass

        self.definir_icone_janela()
        self.geometry("1350x800")
        self.minsize(1024, 680)
        self.configure(bg="#141414")

        # Define o IP recebido da inicialização (se não vier nenhum, usa o padrão)
        self.ip_matriz = ip_matriz if ip_matriz else KUMO_IP_DEFAULT

        # Dispara a checagem de conexão com o IP configurado
        self.testar_conexao_inicial()

        self.config_frequencia = {
            "tipo": "recorrente",
            "dias": [
                "Segunda-feira",
                "Terça-feira",
                "Quarta-feira",
                "Quinta-feira",
                "Sexta-feira",
                "Sábado",
                "Domingo",
            ],
        }

        self.origens_nomes = []
        self.destinos_nomes = []
        self.carregar_labels()

        self.atualizar_listas_combobox()

        self.destino_selecionado = None
        self.origem_selecionada = None
        self.hora_selecionada = "00"
        self.minuto_selecionado = "00"

        self.horas_opcoes = [f"{i:02d} Horas" for i in range(24)]
        self.minutos_opcoes = [f"{i:02d} Minutos" for i in range(60)]

        self.agendamentos = []
        self.agendador_ativo = True

        self.img_logo = None
        self.carregar_logo()

        self.style = ttk.Style()
        temas_disponiveis = self.style.theme_names()
        for tema in ("clam", "alt", "default"):
            if tema in temas_disponiveis:
                try:
                    self.style.theme_use(tema)
                    break
                except Exception:
                    pass

        # Configuração do visual das tabelas
        self.style.configure(
            "Treeview",
            background="#1E1E1E",
            foreground="#FFFFFF",
            fieldbackground="#1E1E1E",
            borderwidth=0,
            rowheight=32,
        )
        self.style.configure(
            "Treeview.Heading",
            background="#2B2B2B",
            foreground="#00E5FF",
            font=("Arial", 13, "bold"),
            borderwidth=0,
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#00E5FF")],
            foreground=[("selected", "#000000")],
        )

        self.navbar = tk.Frame(self, bg="#1E1E1E", height=45)
        self.navbar.pack(fill="x", side="top")

        self.botoes_nav = {}
        self.abas_frames = {}

        abas_config = [
            ("agendar", self.tr("tab_schedule")),
            ("monitor", self.tr("tab_monitor")),
            ("logs", self.tr("tab_logs")),
            ("config", self.tr("tab_config")),
        ]

        self.container_principal = tk.Frame(self, bg="#141414")
        self.container_principal.pack(expand=True, fill="both")

        for key, titulo in abas_config:
            frame_aba = tk.Frame(self.container_principal, bg="#141414")
            self.abas_frames[key] = frame_aba

            btn_frame = tk.Frame(self.navbar, bg="#1E1E1E")
            btn_frame.pack(side="left")

            btn = tk.Button(
                btn_frame,
                text=titulo,
                font=("Arial", 13, "bold"),
                bg="#1E1E1E",
                fg="#A0A0A0",
                activebackground="#1E1E1E",
                activeforeground="#FFFFFF",
                bd=0,
                padx=20,
                pady=10,
                cursor="hand2",
                command=lambda k=key: self.trocar_aba(k),
            )
            btn.pack(side="top")

            indicator = tk.Frame(btn_frame, bg="#1E1E1E", height=3)
            indicator.pack(fill="x", side="bottom")

            btn.bind(
                "<Enter>", lambda e, b=btn, k=key: self._hover_nav(b, k, True)
            )
            btn.bind(
                "<Leave>", lambda e, b=btn, k=key: self._hover_nav(b, k, False)
            )

            self.botoes_nav[key] = {"button": btn, "indicator": indicator}

        self.tab_agendador = self.abas_frames["agendar"]
        self.tab_monitoramento = self.abas_frames["monitor"]
        self.tab_logs = self.abas_frames["logs"]
        self.tab_config = self.abas_frames["config"]

        # 1. Primeiro lê do JSON para self.agendamentos
        self.carregar_agendamentos()

        # 2. Constrói a interface e a Treeview (self.tree)
        self.criar_aba_agendador()
        self.criar_aba_monitoramento()
        self.criar_aba_logs()
        self.criar_aba_configuracoes()

        # 3. Chama explicitamente a função exata de atualizar e desenhar a tabela
        self.atualizar_tabela_e_agendamentos()

        # 4. Ativa a aba inicial
        self.aba_ativa = None
        self.trocar_aba("agendar")

        threading.Thread(target=self.loop_agendador, daemon=True).start()
        logging.info(self.tr("log_initialized"))

        aplicar_icone(self)

    def tr(self, key, **kwargs):
        """Busca e traduz a chave com base no idioma ativo."""
        lang_dict = LOCALES.get(self.idioma_atual, LOCALES["en_US"])
        text = lang_dict.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

    def testar_conexao_inicial(self):
        """Verifica a conectividade com a matriz KUMO durante o startup do app."""

        def worker():
            url = f"http://{self.ip_matriz}/config"
            headers = {
                "Accept": "*/*",
                "User-Agent": "Mozilla/5.0",
                "X-Requested-With": "XMLHttpRequest",
            }
            params = {
                "action": "get",
                "configid": "0",
                "paramid": "eParamID_SysName",
            }
            try:
                logging.info(self.tr("log_init_testing_conn", ip=self.ip_matriz))
                res = requests.get(
                    url, params=params, headers=headers, timeout=3.0
                )
                if res.status_code == 200:
                    logging.info(self.tr("log_init_conn_success", ip=self.ip_matriz))
                else:
                    logging.warning(
                        self.tr("log_init_conn_status", ip=self.ip_matriz, status=res.status_code)
                    )
            except requests.exceptions.ConnectTimeout:
                logging.error(self.tr("log_init_conn_timeout", ip=self.ip_matriz))
            except requests.exceptions.RequestException as err:
                logging.error(self.tr("log_init_conn_failed", ip=self.ip_matriz, err=err))

        threading.Thread(target=worker, daemon=True).start()

    def salvar_configuracao_ip(self):
        """Valida e salva o IP da matriz KUMO no arquivo de configuração."""
        novo_ip = self.entry_ip.get().strip()
        if not novo_ip:
            messagebox.showwarning(self.tr("warning"), self.tr("msg_empty_ip"))
            return

        self.ip_matriz = novo_ip
        self.lbl_status_ip.config(text=f"{self.tr('label_ip_in_use')}: {self.ip_matriz}")

        config_data = {}
        if os.path.exists(self.arquivo_config):
            try:
                with open(self.arquivo_config, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                pass

        config_data["ip_matriz"] = self.ip_matriz

        try:
            with open(self.arquivo_config, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            
            # Utiliza a tradução passando o IP
            logging.info(self.tr("log_ip_saved", ip=self.ip_matriz))
            messagebox.showinfo(self.tr("success"), self.tr("msg_ip_updated", ip=self.ip_matriz))
        except Exception as e:
            logging.error(self.tr("log_ip_save_error", err=e))
            messagebox.showerror(self.tr("error"), f"{self.tr('msg_ip_save_failed')}: {e}")

    def _criar_lista_gerenciador_64(self, parent_frame, lista_nomes, tipo):
        """Cria a tabela e botões de edição rápida dos rótulos (64 portas)."""
        container = tk.Frame(parent_frame, bg="#2B2B2B")
        container.pack(fill="both", expand=True)

        cols = ("num", "nome")
        tree = ttk.Treeview(
            container, columns=cols, show="headings", height=15
        )
        tree.heading("num", text="Porta")
        tree.heading("nome", text=f"Nome da {tipo}")
        tree.column("num", width=60, anchor="center")
        tree.column("nome", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def popular_tabela():
            tree.delete(*tree.get_children())
            for idx, nome in enumerate(lista_nomes):
                tree.insert("", "end", values=(f"{idx + 1:02d}", nome))

        popular_tabela()

        def editar_item(event=None):
            selected = tree.selection()
            if not selected:
                return
            item = tree.item(selected[0])
            porta_num = int(item["values"][0])
            nome_atual = item["values"][1]

            novo_nome = simpledialog.askstring(
                f"Editar {tipo} {porta_num:02d}",
                f"Novo nome para a porta {porta_num:02d}:",
                initialvalue=nome_atual,
                parent=self,
            )

            if novo_nome is not None and novo_nome.strip():
                lista_nomes[porta_num - 1] = novo_nome.strip()
                popular_tabela()
                self.salvar_labels()
                self.atualizar_listas_combobox()

        tree.bind("<Double-1>", editar_item)

        btn_editar = HoverButton(
            parent_frame,
            text=f"EDITAR NOME DA {tipo.upper()}",
            bg_normal="#00E5FF",
            bg_hover="#33EBFB",
            fg_normal="#000000",
            fg_hover="#000000",
            font=("Arial", 9, "bold"),
            pady=4,
            command=editar_item,
        )
        btn_editar.pack(fill="x", pady=(10, 0))

    def criar_aba_configuracoes(self):
        """Cria e configura o painel de configurações na aba correspondente."""
        frame_config = tk.Frame(self.tab_config, bg="#141414")
        frame_config.pack(expand=True, fill="both", padx=20, pady=20)

        # --- SEÇÃO 1: CONFIGURAÇÃO DE IP DA MATRIZ KUMO ---
        frame_ip = tk.LabelFrame(
            frame_config,
            text=f" {self.tr('settings_net_config_title')} ",
            font=("Arial", 12, "bold"),
            fg="#00E5FF",
            bg="#2B2B2B",
            bd=0,
            padx=15,
            pady=15,
        )
        frame_ip.pack(fill="x", pady=(0, 15))

        tk.Label(
            frame_ip,
            text=self.tr("settings_ip_label"),
            font=("Arial", 11, "bold"),
            fg="#FFFFFF",
            bg="#2B2B2B",
        ).pack(side="left", padx=(0, 10))

        self.entry_ip = tk.Entry(
            frame_ip,
            font=("Arial", 12),
            bg="#1E1E1E",
            fg="#00FF66",
            bd=0,
            highlightthickness=1,
            highlightbackground="#444444",
            insertbackground="#FFFFFF",
            width=20,
        )
        self.entry_ip.pack(side="left", padx=(0, 15))
        self.entry_ip.insert(0, getattr(self, "ip_matriz", "192.168.1.101"))

        btn_salvar_ip = HoverButton(
            frame_ip,
            text=self.tr("settings_btn_save_ip"),
            bg_normal="#00E5FF",
            bg_hover="#33EBFB",
            fg_normal="#000000",
            fg_hover="#000000",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=4,
            command=self.salvar_configuracao_ip,
        )
        btn_salvar_ip.pack(side="left")

        self.lbl_status_ip = tk.Label(
            frame_ip,
            text=f"{self.tr('settings_ip_in_use')} {getattr(self, 'ip_matriz', '192.168.1.101')}",
            font=("Arial", 10, "italic"),
            fg="#A0A0A0",
            bg="#2B2B2B",
        )
        self.lbl_status_ip.pack(side="right", padx=10)

        # --- SEÇÃO 2: RÓTULOS DAS PORTAS (64 ENTRADAS E 64 SAÍDAS) ---
        frame_listas = tk.Frame(frame_config, bg="#141414")
        frame_listas.pack(fill="both", expand=True)

        frame_origens = tk.LabelFrame(
            frame_listas,
            text=f" {self.tr('settings_inputs_title')} ",
            font=("Arial", 11, "bold"),
            fg="#00E5FF",
            bg="#2B2B2B",
            bd=0,
            padx=10,
            pady=10,
        )
        frame_origens.pack(side="left", fill="both", expand=True, padx=(0, 10))

        frame_destinos = tk.LabelFrame(
            frame_listas,
            text=f" {self.tr('settings_outputs_title')} ",
            font=("Arial", 11, "bold"),
            fg="#00E5FF",
            bg="#2B2B2B",
            bd=0,
            padx=10,
            pady=10,
        )
        frame_destinos.pack(
            side="right", fill="both", expand=True, padx=(10, 0)
        )

        self._criar_lista_gerenciador_64(
            frame_origens, self.origens_nomes, "Origem"
        )
        self._criar_lista_gerenciador_64(
            frame_destinos, self.destinos_nomes, "Destino"
        )


    def carregar_labels(self):
        origens_raw = None
        destinos_raw = None

        if os.path.exists(JSON_LABELS_FILE):
            try:
                with open(JSON_LABELS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    origens_raw = data.get("origens")
                    destinos_raw = data.get("destinos")
            except Exception as e:
                logging.error(f"Falha ao carregar rótulos do arquivo: {e}")

        if origens_raw is None:
            origens_raw = ORIGENS_NOMES_DEFAULT
        if destinos_raw is None:
            destinos_raw = DESTINOS_NOMES_DEFAULT

        # Normaliza e traduz dinamicamente as 64 portas de Entrada (Origens)
        self.origens_nomes = {}
        for i in range(1, 65):
            nome_raw = origens_raw.get(i) or origens_raw.get(str(i), f"default_input_label:{i}")
            self.origens_nomes[i] = obter_nome_porta(str(nome_raw))

        # Normaliza e traduz dinamicamente as 64 portas de Saída (Destinos)
        self.destinos_nomes = {}
        for i in range(1, 65):
            nome_raw = destinos_raw.get(i) or destinos_raw.get(str(i), f"default_output_label:{i}")
            self.destinos_nomes[i] = obter_nome_porta(str(nome_raw))

    def salvar_labels(self):
        try:
            data = {
                "origens": self.origens_nomes,
                "destinos": self.destinos_nomes,
            }
            with open(JSON_LABELS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Falha ao salvar rótulos no disco: {e}")

    def _normalizar_64_portas(self, fonte_dados, prefixo_padrao):
        lista_resultado = []
        for i in range(64):
            num_porta = i + 1
            nome = None

            if isinstance(fonte_dados, dict):
                nome = fonte_dados.get(
                    num_porta, fonte_dados.get(str(num_porta))
                )
            elif isinstance(fonte_dados, (list, tuple)):
                if i < len(fonte_dados):
                    nome = fonte_dados[i]

            if nome is not None:
                nome = str(nome).strip()
                if nome.startswith("[") and "]" in nome:
                    nome = nome.split("]", 1)[1].strip()

            if not nome:
                nome = f"{prefixo_padrao} {num_porta:02d}"

            lista_resultado.append(nome)

        return lista_resultado

    def trocar_aba(self, chave_aba):
        if self.aba_ativa == chave_aba:
            return

        for k, f in self.abas_frames.items():
            f.pack_forget()

        self.abas_frames[chave_aba].pack(expand=True, fill="both")
        self.aba_ativa = chave_aba

        for k, item in self.botoes_nav.items():
            if k == chave_aba:
                item["button"].configure(fg="#00E5FF")
                item["indicator"].configure(bg="#00E5FF")
            else:
                item["button"].configure(fg="#A0A0A0")
                item["indicator"].configure(bg="#1E1E1E")

    def _hover_nav(self, btn, key, entrada):
        if key != self.aba_ativa:
            btn.configure(fg="#FFFFFF" if entrada else "#A0A0A0")

    def atualizar_listas_combobox(self):
        self.origens_combo = [
            f"[{i+1:02d}] {nome}" for i, nome in enumerate(self.origens_nomes)
        ]
        self.destinos_combo = [
            f"[{i+1:02d}] {nome}" for i, nome in enumerate(self.destinos_nomes)
        ]

    def definir_icone_janela(self):
        try:
            caminho_ico = resource_path("logo.ico")
            if os.path.exists(caminho_ico):
                self.iconbitmap(caminho_ico)
        except Exception as e:
            logging.warning(f"Não foi possível carregar o ícone da janela: {e}")

    def carregar_logo(self):
        caminho_logo = resource_path("logo.png")
        if os.path.exists(caminho_logo):
            try:
                img_pil = Image.open(caminho_logo)
                img_pil.thumbnail((280, 100))
                self.img_logo = ImageTk.PhotoImage(img_pil)
            except Exception as e:
                logging.error(f"Erro ao carregar imagem da logo: {e}")
                self.img_logo = None

    def carregar_agendamentos(self):
        if os.path.exists("agendamentos.json"):
            try:
                with open("agendamentos.json", "r", encoding="utf-8") as f:
                    self.agendamentos = json.load(f)

                houve_alteracao = False

                # Garante que todo registro tenha um UUID interno único
                for item in self.agendamentos:
                    if "uuid" not in item:
                        item["uuid"] = str(uuid.uuid4())
                        houve_alteracao = True

                # Reorganiza os IDs numéricos visuais em sequência (1, 2, 3...)
                for idx, item in enumerate(self.agendamentos, start=1):
                    if item.get("id") != idx:
                        item["id"] = idx
                        houve_alteracao = True

                if houve_alteracao:
                    self.salvar_agendamentos()

            except Exception as e:
                logging.error(
                    f"Erro ao carregar o arquivo agendamentos.json: {e}"
                )
                self.agendamentos = []
        else:
            self.agendamentos = []

    def salvar_agendamentos(self):
        try:
            with open(JSON_AGENDAMENTOS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.agendamentos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Falha ao salvar agendamentos no disco: {e}")

    def definir_horario_atual(self):
        agora = time.localtime()
        self.hora_selecionada = f"{agora.tm_hour:02d}"
        self.minuto_selecionado = f"{agora.tm_min:02d}"
        self.btn_hora.config(text=f"{self.hora_selecionada} h")
        self.btn_minuto.config(text=f"{self.minuto_selecionado} m")

    def redefinir_campos_interface(self):
        self.btn_destino.config(
            text=self.tr("placeholder_select_destination")
        )
        self.btn_origem.config(text=self.tr("placeholder_select_source"))

        txt_freq = self.formatar_texto_frequencia(
            self.config_frequencia.get("dias", [])
        )
        self.btn_dias.config(text=txt_freq)

        self.btn_hora.config(text=f"00 {self.tr('unit_hours')}")
        self.btn_minuto.config(text=f"00 {self.tr('unit_minutes')}")

    def resetar_formulario(self):
        self.destino_selecionado = None
        self.origem_selecionada = None
        self.hora_selecionada = "00"
        self.minuto_selecionado = "00"
        self.config_frequencia = {
            "tipo": "recorrente",
            "dias": [
                "Segunda-feira",
                "Terça-feira",
                "Quarta-feira",
                "Quinta-feira",
                "Sexta-feira",
                "Sábado",
                "Domingo",
            ],
        }
        self.id_agendamento_em_edicao = None
        self.btn_add.config(text=self.tr("btn_add_schedule_action"))
        self.redefinir_campos_interface()

    def _definir_destino(self, valor):
        self.destino_selecionado = valor
        self.btn_destino.config(
            text=valor if valor else self.tr("placeholder_select_destination")
        )

    def _definir_origem(self, valor):
        self.origem_selecionada = valor
        self.btn_origem.config(
            text=valor if valor else self.tr("placeholder_select_source")
        )

    def _definir_hora(self, valor):
        hora_num = sanitizar_tempo(valor)
        self.hora_selecionada = hora_num
        self.btn_hora.config(text=f"{hora_num} {self.tr('unit_hours')}")

    def _definir_minuto(self, valor):
        minuto_num = sanitizar_tempo(valor)
        self.minuto_selecionado = minuto_num
        self.btn_minuto.config(text=f"{minuto_num} {self.tr('unit_minutes')}")

    def criar_aba_agendador(self):
        topo_frame = tk.Frame(self.tab_agendador, bg="#141414")
        topo_frame.pack(fill="x", pady=(15, 5))

        if self.img_logo:
            lbl = tk.Label(topo_frame, image=self.img_logo, bg="#141414")
            lbl.pack()
        else:
            lbl = tk.Label(
                topo_frame,
                text="AjaSchedule",
                font=("Arial", 18, "bold"),
                bg="#141414",
                fg="#FFFFFF",
            )
            lbl.pack()

        frame_top = tk.LabelFrame(
            self.tab_agendador,
            text=f" {self.tr('frame_new_schedule')} ",
            font=("Arial", 13, "bold"),
            fg="#00E5FF",
            bg="#2B2B2B",
            bd=0,
            padx=15,
            pady=15,
        )
        frame_top.pack(fill="x", padx=20, pady=10)

        tk.Label(
            frame_top,
            text=self.tr("lbl_destination"),
            bg="#2B2B2B",
            fg="#FFFFFF",
            font=("Arial", 11, "bold"),
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.btn_destino = HoverButton(
            frame_top,
            text=self.tr("placeholder_select_destination"),
            bg_normal="#1E1E1E",
            bg_hover="#3A3A3A",
            fg_normal="#00E5FF",
            fg_hover="#00E5FF",
            font=("Arial", 11, "bold"),
            width=22,
            pady=4,
            command=self.abrir_seletor_destino,
        )
        self.btn_destino.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(
            frame_top,
            text=self.tr("lbl_source"),
            bg="#2B2B2B",
            fg="#FFFFFF",
            font=("Arial", 11, "bold"),
        ).grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.btn_origem = HoverButton(
            frame_top,
            text=self.tr("placeholder_select_source"),
            bg_normal="#1E1E1E",
            bg_hover="#3A3A3A",
            fg_normal="#00E5FF",
            fg_hover="#00E5FF",
            font=("Arial", 11, "bold"),
            width=22,
            pady=4,
            command=self.abrir_seletor_origem,
        )
        self.btn_origem.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(
            frame_top,
            text=self.tr("lbl_frequency"),
            bg="#2B2B2B",
            fg="#FFFFFF",
            font=("Arial", 11, "bold"),
        ).grid(row=0, column=4, padx=5, pady=5, sticky="e")

        self.btn_dias = HoverButton(
            frame_top,
            text=self.formatar_texto_frequencia(
                self.config_frequencia.get("dias", [])
            ),
            bg_normal="#1E1E1E",
            bg_hover="#3A3A3A",
            fg_normal="#00E5FF",
            fg_hover="#00E5FF",
            font=("Arial", 11, "bold"),
            padx=8,
            pady=4,
            command=self.abrir_seletor_dias,
        )
        self.btn_dias.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(
            frame_top,
            text=self.tr("lbl_time"),
            bg="#2B2B2B",
            fg="#FFFFFF",
            font=("Arial", 11, "bold"),
        ).grid(row=0, column=6, padx=5, pady=5, sticky="e")

        frame_horario = tk.Frame(frame_top, bg="#2B2B2B")
        frame_horario.grid(row=0, column=7, padx=5, pady=5)

        self.btn_hora = HoverButton(
            frame_horario,
            text=f"00 {self.tr('unit_hours')}",
            bg_normal="#1E1E1E",
            bg_hover="#3A3A3A",
            fg_normal="#00E5FF",
            fg_hover="#00E5FF",
            font=("Arial", 11, "bold"),
            width=5,
            pady=4,
            command=self.abrir_seletor_hora,
        )
        self.btn_hora.pack(side="left")

        tk.Label(
            frame_horario,
            text=":",
            bg="#2B2B2B",
            fg="#FFFFFF",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=2)

        self.btn_minuto = HoverButton(
            frame_horario,
            text=f"00 {self.tr('unit_minutes')}",
            bg_normal="#1E1E1E",
            bg_hover="#3A3A3A",
            fg_normal="#00E5FF",
            fg_hover="#00E5FF",
            font=("Arial", 11, "bold"),
            width=5,
            pady=4,
            command=self.abrir_seletor_minuto,
        )
        self.btn_minuto.pack(side="left", padx=(0, 5))

        btn_agora = HoverButton(
            frame_horario,
            text=self.tr("btn_now"),
            bg_normal="#3A3A3A",
            bg_hover="#555555",
            fg_normal="#00E5FF",
            fg_hover="#FFFFFF",
            font=("Arial", 11, "bold"),
            padx=4,
            pady=4,
            command=self.definir_horario_atual,
        )
        btn_agora.pack(side="left")

        self.btn_add = HoverButton(
            frame_top,
            text=self.tr("btn_add_schedule_action"),
            bg_normal="#00E5FF",
            bg_hover="#33EBFB",
            fg_normal="#000000",
            fg_hover="#000000",
            font=("Arial", 11, "bold"),
            padx=14,
            pady=5,
            command=self.adicionar_agendamento,
        )
        self.btn_add.grid(row=0, column=8, padx=15, pady=5)
        self.btn_add.bind(
            "<Return>", lambda event: self.adicionar_agendamento()
        )

        # Container Isolado para Tabela e Scrollbar
        frame_tabela = tk.Frame(self.tab_agendador, bg="#141414")
        frame_tabela.pack(expand=True, fill="both", padx=20, pady=(0, 5))

        cols = ("ID", "Destino", "Origem", "Frequencia", "Horario", "Status")
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=cols,
            show="headings",
            height=10,
            selectmode="extended",
        )

        # Configuração dos cabeçalhos das colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Destino", text=self.tr("col_destination"))
        self.tree.heading("Origem", text=self.tr("col_source"))
        self.tree.heading("Frequencia", text=self.tr("col_frequency"))
        self.tree.heading("Horario", text=self.tr("col_time"))
        self.tree.heading("Status", text=self.tr("col_status"))

        # Configuração das larguras e alinhamentos
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Destino", width=250, anchor="w")
        self.tree.column("Origem", width=250, anchor="w")
        self.tree.column("Frequencia", width=200, anchor="center")
        self.tree.column("Horario", width=100, anchor="center")
        self.tree.column("Status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(
            frame_tabela, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<Double-1>", lambda event: self.carregar_agendamento_para_edicao()
        )

        # RODAPÉ COM OS BOTÕES DE AÇÃO
        frame_botoes_acoes = tk.Frame(self.tab_agendador, bg="#141414")
        frame_botoes_acoes.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_editar = HoverButton(
            frame_botoes_acoes,
            text=self.tr("btn_edit_selected"),
            bg_normal="#2B2B2B",
            bg_hover="#3E3E3E",
            fg_normal="#FFFFFF",
            fg_hover="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            command=self.carregar_agendamento_para_edicao,
        )
        self.btn_editar.pack(side="left", padx=(0, 5))

        self.btn_remover = HoverButton(
            frame_botoes_acoes,
            text=self.tr("btn_remove_selected"),
            bg_normal="#FF5252",
            bg_hover="#FF7373",
            fg_normal="#FFFFFF",
            fg_hover="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            command=self.remover_agendamento,
        )
        self.btn_remover.pack(side="left", padx=5)

        self.btn_executar = HoverButton(
            frame_botoes_acoes,
            text=self.tr("btn_run_now"),
            bg_normal="#00E5FF",
            bg_hover="#33EBFB",
            fg_normal="#000000",
            fg_hover="#000000",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            command=self.forcar_execucao_agora,
        )
        self.btn_executar.pack(side="right", padx=(5, 0))

    def carregar_agendamento_para_edicao(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                self.tr("msg_select_item_title"),
                self.tr("msg_select_item_edit")
            )
            return

        item_values = self.tree.item(selected_items[0], "values")
        item_id = int(item_values[0])

        agendamento = next((a for a in self.agendamentos if a["id"] == item_id), None)
        if not agendamento:
            return

        self.id_agendamento_em_edicao = item_id

        self.destino_selecionado = f"[{agendamento['destino_num']:02d}] {agendamento['destino_nome']}"
        self.origem_selecionada = f"[{agendamento['origem_num']:02d}] {agendamento['origem_nome']}"

        horario_partes = agendamento["horario"].split(":")
        self.hora_selecionada = sanitizar_tempo(horario_partes[0])
        self.minuto_selecionado = sanitizar_tempo(horario_partes[1])

        if agendamento.get("tipo") == "unico":
            self.config_frequencia = {
                "tipo": "unico",
                "data": agendamento.get("data_unica", "")
            }
        else:
            self.config_frequencia = {
                "tipo": "recorrente",
                "dias": agendamento.get("dias_lista", [])
            }

        self.redefinir_campos_interface()
        self.btn_add.config(text=self.tr("btn_save_changes"))

        self.after(150, self.abrir_seletor_destino)

    def abrir_seletor_destino(self):
        def callback_confirmar(valor):
            if valor is not None:
                self._definir_destino(valor)
                self.after(120, self.abrir_seletor_origem)

        def callback_cancelar():
            self.resetar_formulario()

        # ✅ Monta dinamicamente a lista com os labels atualizados (compatível com Dicionário e Lista)
        if isinstance(getattr(self, "destinos_nomes", None), dict):
            destinos_atualizados = [
                f"[{port:02d}] {nome}"
                for port, nome in sorted(self.destinos_nomes.items())
            ]
        else:
            destinos_atualizados = [
                f"[{i+1:02d}] {nome}"
                for i, nome in enumerate(self.destinos_nomes)
            ]

        SeletorCanalPopup(
            self,
            "destino",
            destinos_atualizados,  # ✅ Passa a lista viva e atualizada
            callback_confirmar,
            callback_cancelar=callback_cancelar,
            valor_inicial=self.destino_selecionado
        )

    def abrir_seletor_origem(self):
        def callback_confirmar(valor):
            if valor is not None:
                self._definir_origem(valor)
                self.after(120, self.abrir_seletor_dias)

        def callback_cancelar():
            self.resetar_formulario()

        # ✅ Monta dinamicamente a lista com os labels atualizados (compatível com Dicionário e Lista)
        if isinstance(getattr(self, "origens_nomes", None), dict):
            origens_atualizadas = [
                f"[{port:02d}] {nome}"
                for port, nome in sorted(self.origens_nomes.items())
            ]
        else:
            origens_atualizadas = [
                f"[{i+1:02d}] {nome}"
                for i, nome in enumerate(self.origens_nomes)
            ]

        SeletorCanalPopup(
            self,
            "origem",
            origens_atualizadas,  # ✅ Passa a lista viva e atualizada
            callback_confirmar,
            callback_cancelar=callback_cancelar,
            valor_inicial=self.origem_selecionada
        )

    def abrir_seletor_dias(self):
        def callback_confirmar(nova_config):
            if nova_config is not None:
                self.atualizar_config_frequencia(nova_config)
                self.after(120, self.abrir_seletor_hora)

        def callback_cancelar():
            self.resetar_formulario()

        dias_todos = [
            self.tr("day_monday"),
            self.tr("day_tuesday"),
            self.tr("day_wednesday"),
            self.tr("day_thursday"),
            self.tr("day_friday"),
            self.tr("day_saturday"),
            self.tr("day_sunday")
        ]

        if getattr(self, "id_agendamento_em_edicao", None) is None:
            if not getattr(self, "config_frequencia", None) or not self.config_frequencia.get("dias"):
                self.config_frequencia = {
                    "tipo": "recorrente",
                    "dias": dias_todos.copy()
                }

        SeletorDiasPopup(
            self,
            self.config_frequencia,
            callback_confirmar,
            callback_cancelar=callback_cancelar
        )

    def abrir_seletor_hora(self):
        def callback_confirmar(valor):
            if valor is not None:
                self._definir_hora(valor)
                self.after(120, self.abrir_seletor_minuto)

        def callback_cancelar():
            self.resetar_formulario()

        val_sanitizado = sanitizar_tempo(getattr(self, "hora_selecionada", "00"))
        valor_ini = f"{val_sanitizado} {self.tr('unit_hours_plural')}"
        horas_traduzidas = [f"{h:02d} {self.tr('unit_hours_plural')}" for h in range(24)]

        SeletorCanalPopup(
            self,
            "hora",
            horas_traduzidas,
            callback_confirmar,
            callback_cancelar=callback_cancelar,
            valor_inicial=valor_ini
        )

    def abrir_seletor_minuto(self):
        def callback_confirmar(valor):
            if valor is not None:
                self._definir_minuto(valor)
                self.after(50, lambda: self.btn_add.focus_set())

        def callback_cancelar():
            self.resetar_formulario()

        val_sanitizado = sanitizar_tempo(self.minuto_selecionado)
        valor_ini = f"{val_sanitizado} {self.tr('unit_minutes_plural')}"
        minutos_traduzidos = [f"{m:02d} {self.tr('unit_minutes_plural')}" for m in range(60)]

        SeletorCanalPopup(
            self,
            "minuto",
            minutos_traduzidos,
            callback_confirmar,
            callback_cancelar=callback_cancelar,
            valor_inicial=valor_ini
        )

    def atualizar_config_frequencia(self, nova_config):
        self.config_frequencia = nova_config
        txt = self.formatar_texto_frequencia(nova_config)
        self.btn_dias.config(text=txt)

    def formatar_texto_frequencia(self, config_freq):
        if isinstance(config_freq, dict):
            # Aceita tanto 'unico' quanto 'unica'
            if config_freq.get("tipo") in ("unico", "unica"):
                return self.tr("freq_once")
            config_freq = config_freq.get("dias", [])

        if isinstance(config_freq, (list, set, tuple)) and len(config_freq) == 7:
            return self.tr("freq_everyday")

        if config_freq in ("Todos os Dias", "Every Day"):
            return self.tr("freq_everyday")

        if config_freq in ("Apenas Uma Vez", "Once Only", "Single Date"):
            return self.tr("freq_once")

        dias_map = {
            "Segunda-feira": "day_monday", "Terça-feira": "day_tuesday",
            "Quarta-feira": "day_wednesday", "Quinta-feira": "day_thursday",
            "Sexta-feira": "day_friday", "Sábado": "day_saturday", "Domingo": "day_sunday",
            "Monday": "day_monday", "Tuesday": "day_tuesday",
            "Wednesday": "day_wednesday", "Thursday": "day_thursday",
            "Friday": "day_friday", "Saturday": "day_saturday", "Sunday": "day_sunday",
            "seg": "day_mon_short", "ter": "day_tue_short",
            "qua": "day_wed_short", "qui": "day_thu_short",
            "sex": "day_fri_short", "sab": "day_sat_short", "sáb": "day_sat_short", "dom": "day_sun_short",
            "mon": "day_mon_short", "tue": "day_tue_short",
            "wed": "day_wed_short", "thu": "day_thu_short",
            "fri": "day_fri_short", "sat": "day_sat_short", "sun": "day_sun_short"
        }

        if isinstance(config_freq, str) and "," in config_freq:
            config_freq = [d.strip() for d in config_freq.split(",")]

        if isinstance(config_freq, (list, set, tuple)):
            dias_traduzidos = []
            for d in config_freq:
                d_str = str(d).strip()
                chave_map = dias_map.get(d_str) or dias_map.get(d_str.lower())
                if chave_map:
                    dias_traduzidos.append(self.tr(chave_map))
                else:
                    dias_traduzidos.append(d_str)
            return ", ".join(dias_traduzidos)

        if isinstance(config_freq, str):
            chave_map = dias_map.get(config_freq) or dias_map.get(config_freq.lower())
            if chave_map:
                return self.tr(chave_map)

        return str(config_freq)
    
    def adicionar_agendamento(self):
        try:
            # 1. Validação de seleção de Destino e Origem
            if not getattr(self, "destino_selecionado", None):
                messagebox.showwarning(
                    self.tr("msg_select_item_title"), 
                    self.tr("placeholder_select_destination")
                )
                return

            if not getattr(self, "origem_selecionada", None):
                messagebox.showwarning(
                    self.tr("msg_select_item_title"), 
                    self.tr("placeholder_select_source")
                )
                return

            # 2. Validação de Horário e Frequência
            if not getattr(self, "hora_selecionada", None) or not getattr(self, "minuto_selecionado", None):
                messagebox.showwarning(
                    self.tr("msg_select_item_title"), 
                    self.tr("title_select_hour")
                )
                return

            if not getattr(self, "config_frequencia", None):
                messagebox.showwarning(
                    self.tr("msg_select_item_title"), 
                    self.tr("header_freq_routine")
                )
                return

            # 3. Extração dos índices numéricos de Destino e Origem
            m_dest = re.search(r"\[(\d+)\]", self.destino_selecionado)
            m_orig = re.search(r"\[(\d+)\]", self.origem_selecionada)

            dest_num = int(m_dest.group(1)) if m_dest else 1
            orig_num = int(m_orig.group(1)) if m_orig else 1

            # ✅ CORRIGIDO: Acesso direto por chave (1 a 64) no dicionário
            dest_nome = self.destinos_nomes.get(dest_num, f"Destino {dest_num:02d}")
            orig_nome = self.origens_nomes.get(orig_num, f"Origem {orig_num:02d}")

            # 4. Formatação de tempo e frequência
            hora_fmt = sanitizar_tempo(self.hora_selecionada)
            minuto_fmt = sanitizar_tempo(self.minuto_selecionado)
            horario = f"{hora_fmt}:{minuto_fmt}:00"

            frequencia_fmt = self.formatar_texto_frequencia(self.config_frequencia)

            tipo_agendamento = self.config_frequencia.get("tipo", "recorrente")
            dias_lista = self.config_frequencia.get("dias", []) if tipo_agendamento == "recorrente" else []
            data_unica = self.config_frequencia.get("data", "") if tipo_agendamento == "unico" else ""

            # Prepara string "às" / "at" / "a las" conforme o idioma
            str_time_at = self.tr("log_time_at")

            # 5. Fluxo de Edição ou Criação
            if getattr(self, "id_agendamento_em_edicao", None) is not None:
                item = next((a for a in self.agendamentos if a["id"] == self.id_agendamento_em_edicao), None)
                if item:
                    # Dados anteriores
                    ant_dest = f"[{item['destino_num']:02d}] {item['destino_nome']}"
                    ant_orig = f"[{item['origem_num']:02d}] {item['origem_nome']}"
                    ant_freq = item.get("frequencia", "")
                    ant_hora = item.get("horario", "")
                    
                    time_old_str = f"{ant_freq} {ant_hora}"

                    # Novos dados
                    novo_dest = f"[{dest_num:02d}] {dest_nome}"
                    novo_orig = f"[{orig_num:02d}] {orig_nome}"
                    time_new_str = f"{frequencia_fmt} {horario}"

                    if "uuid" not in item or not item["uuid"]:
                        item["uuid"] = str(uuid.uuid4())

                    horario_mudou = item.get("horario") != horario or item.get("frequencia") != frequencia_fmt

                    item.update({
                        "destino_num": dest_num,
                        "destino_nome": dest_nome,
                        "origem_num": orig_num,
                        "origem_nome": orig_nome,
                        "tipo": tipo_agendamento,
                        "dias_lista": list(dias_lista),
                        "data_unica": data_unica,
                        "frequencia": frequencia_fmt,
                        "horario": horario,
                        "executado_hoje": False if horario_mudou else item.get("executado_hoje", False),
                        "ultimo_dia_executado": "" if horario_mudou else item.get("ultimo_dia_executado", ""),
                    })

                    # Log de Atualização Traduzido
                    msg_log = self.tr(
                        "log_routine_updated",
                        id=self.id_agendamento_em_edicao,
                        uuid=item["uuid"][:8],
                        dest_old=ant_dest,
                        src_old=ant_orig,
                        time_at=str_time_at,
                        time_old=time_old_str,
                        dest_new=novo_dest,
                        src_new=novo_orig,
                        time_new=time_new_str
                    )
                    logging.info(msg_log)
            else:
                # Criação de novo agendamento
                item_id = max([a["id"] for a in self.agendamentos], default=0) + 1
                item_uuid = str(uuid.uuid4())

                item_data = {
                    "id": item_id,
                    "uuid": item_uuid,
                    "destino_num": dest_num,
                    "destino_nome": dest_nome,
                    "origem_num": orig_num,
                    "origem_nome": orig_nome,
                    "tipo": tipo_agendamento,
                    "dias_lista": list(dias_lista),
                    "data_unica": data_unica,
                    "frequencia": frequencia_fmt,
                    "horario": horario,
                    "executado_hoje": False,
                    "ultimo_dia_executado": "",
                }

                self.agendamentos.append(item_data)

                # Log de Criação Traduzido
                str_dest = f"[{dest_num:02d}] {dest_nome}"
                str_orig = f"[{orig_num:02d}] {orig_nome}"

                msg_log = self.tr(
                    "log_routine_added",
                    id=item_id,
                    uuid=item_uuid[:8],
                    dest=str_dest,
                    src=str_orig,
                    time_at=str_time_at,
                    time=horario,
                    freq=frequencia_fmt
                )
                logging.info(msg_log)

            # 6. Finalização e persistência
            self.salvar_agendamentos()
            self.atualizar_tabela_e_agendamentos()
            self.atualizar_painel_monitoramento()
            self.resetar_formulario()

        except Exception as e:
            logging.error(f"Erro inesperado ao salvar agendamento: {e}", exc_info=True)
            messagebox.showerror("Erro", f"Falha ao processar agendamento:\n{e}")

    def remover_agendamento(self, item_ids=None):
        # ✅ Se for um evento enviado pelo Tkinter (.bind), ignora e trata como None
        if hasattr(item_ids, "widget") or type(item_ids).__name__ == "Event":
            item_ids = None

        str_time_at = self.tr("log_time_at")

        if item_ids is not None:
            # Remoção direta (ex: eventos únicos pós-execução). Aceita int (ID), str (UUID) ou lista de ambos.
            if isinstance(item_ids, (int, str)):
                item_ids = [item_ids]

            for id_ou_uuid in item_ids:
                # Procura o item tanto por ID numérico quanto por UUID
                item_removido = next(
                    (a for a in self.agendamentos if a.get("id") == id_ou_uuid or a.get("uuid") == id_ou_uuid),
                    None
                )
                if item_removido:
                    target_uuid = item_removido.get("uuid", "")
                    str_dest = f"[{item_removido['destino_num']:02d}] {item_removido['destino_nome']}"
                    str_orig = f"[{item_removido['origem_num']:02d}] {item_removido['origem_nome']}"

                    msg_log = self.tr(
                        "log_single_event_removed",
                        id=item_removido['id'],
                        uuid=target_uuid[:8],
                        dest=str_dest,
                        src=str_orig,
                        time_at=str_time_at,
                        time=item_removido['horario'],
                        freq=item_removido['frequencia']
                    )
                    logging.info(msg_log)

                    # Exclui usando estritamente a chave UUID única
                    self.agendamentos = [a for a in self.agendamentos if a.get("uuid") != target_uuid]

            # Reordena a numeração visual sequencial (1, 2, 3...) dos itens restantes
            for idx, item in enumerate(self.agendamentos, start=1):
                item["id"] = idx

            self.salvar_agendamentos()
            self.atualizar_tabela_e_agendamentos()
            self.atualizar_painel_monitoramento()
            return

        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                self.tr("msg_select_item_title"),
                self.tr("msg_select_item_delete")
            )
            return

        todos_itens = self.tree.get_children()
        ultimo_selecionado = selected_items[-1]
        idx_ultimo = todos_itens.index(ultimo_selecionado)

        for sel in selected_items:
            item_values = self.tree.item(sel, "values")
            item_id_visual = int(item_values[0])

            # Localiza o registro correspondente ao ID visual selecionado na Treeview
            item_removido = next((a for a in self.agendamentos if a["id"] == item_id_visual), None)
            if item_removido:
                target_uuid = item_removido.get("uuid", "")
                str_dest = f"[{item_removido['destino_num']:02d}] {item_removido['destino_nome']}"
                str_orig = f"[{item_removido['origem_num']:02d}] {item_removido['origem_nome']}"

                msg_log = self.tr(
                    "log_routine_removed",
                    id=item_id_visual,
                    uuid=target_uuid[:8],
                    dest=str_dest,
                    src=str_orig,
                    time_at=str_time_at,
                    time=item_removido['horario'],
                    freq=item_removido['frequencia']
                )
                logging.info(msg_log)

                # Remove da memória pelo UUID real
                self.agendamentos = [a for a in self.agendamentos if a.get("uuid") != target_uuid]

        # Reordena os IDs numéricos visuais após a exclusão dos selecionados
        for idx, item in enumerate(self.agendamentos, start=1):
            item["id"] = idx

        self.salvar_agendamentos()
        self.atualizar_tabela_e_agendamentos() # Atualiza a Treeview com os IDs visuais renovados
        self.atualizar_painel_monitoramento()

        itens_restantes = self.tree.get_children()
        if itens_restantes:
            novo_idx = min(idx_ultimo, len(itens_restantes) - 1)
            proximo_item = itens_restantes[novo_idx]

            self.tree.selection_set(proximo_item)
            self.tree.focus(proximo_item)
            self.tree.see(proximo_item)

    def forcar_execucao_agora(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                self.tr("msg_select_item_title"),
                self.tr("msg_select_item_run")
            )
            return

        itens_selecionados = selected_item if isinstance(selected_item, (list, tuple)) else [selected_item]

        origem_acao_traduzida = self.tr("log_forced_manual")

        for sel in itens_selecionados:
            # 1. Tenta identificar primeiro pelo UUID do iid da Treeview
            item = next((a for a in self.agendamentos if a.get("uuid") == sel), None)

            # 2. Se não encontrar pelo UUID, busca pelo ID visual da 1ª coluna
            if not item:
                item_values = self.tree.item(sel, "values")
                if item_values and len(item_values) > 0:
                    try:
                        item_id = int(item_values[0])
                        item = next((a for a in self.agendamentos if a.get("id") == item_id), None)
                    except (ValueError, TypeError):
                        pass

            # 3. Dispara a comutação usando fallbacks localizados
            if item:
                nome_dest_default = f"{self.tr('label_destination')} {item['destino_num']:02d}"
                nome_orig_default = f"{self.tr('label_source')} {item['origem_num']:02d}"
                tipo_agendamento_default = self.tr("type_recurrent")

                self.comutar_input(
                    item_id=item.get("id"),
                    posicao_destino=item["destino_num"],
                    entrada_origem=item["origem_num"],
                    nome_destino=item.get("destino_nome", nome_dest_default),
                    nome_origem=item.get("origem_nome", nome_orig_default),
                    origem_acao=origem_acao_traduzida,
                    tipo_agendamento=item.get("tipo", tipo_agendamento_default)
                )
            else:
                logging.warning(f"Item selecionado na tabela ({sel}) não foi localizado na memória.")

    def criar_aba_monitoramento(self):
        frame_info = tk.Frame(self.tab_monitoramento, bg="#141414")
        frame_info.pack(fill="x", padx=20, pady=10)

        lbl_tit = tk.Label(
            frame_info,
            text=self.tr("rt_panel_title"),
            font=("Arial", 14, "bold"),
            fg="#00E5FF",
            bg="#141414",
        )
        lbl_tit.pack(side="left")

        self.frame_cards_scroll = tk.Frame(self.tab_monitoramento, bg="#141414")
        self.frame_cards_scroll.pack(expand=True, fill="both", padx=20, pady=10)

        self.canvas = tk.Canvas(
            self.frame_cards_scroll, bg="#141414", highlightthickness=0
        )
        scrollbar_mon = ttk.Scrollbar(
            self.frame_cards_scroll, orient="vertical", command=self.canvas.yview
        )

        self.container_cards = tk.Frame(self.canvas, bg="#141414")
        self.container_cards.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.container_cards, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_mon.set)

        self.canvas.pack(side="left", expand=True, fill="both")
        scrollbar_mon.pack(side="right", fill="y")

        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfig(self.canvas_window_id, width=event.width)
        )

        self._bind_mousewheel_area(self.canvas)
        self._bind_mousewheel_area(self.container_cards)

        self.atualizar_painel_monitoramento()

    def _on_mousewheel(self, event):
        if sys.platform == "win32":
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif sys.platform == "darwin":
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel_area(self, widget):
        widget.bind("<Enter>", lambda e: self._ativar_mousewheel())
        widget.bind("<Leave>", lambda e: self._desativar_mousewheel())

    def _ativar_mousewheel(self):
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

    def _desativar_mousewheel(self):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _formatar_frequencia_exibicao(self, freq_str):
        """Traduz os termos de frequência salvos para o idioma selecionado."""
        if not freq_str:
            return ""

        freq_str_clean = str(freq_str).strip()

        # Checagens diretas insensíveis a maiúsculas/minúsculas
        freq_upper = freq_str_clean.upper()
        if freq_upper in ("TODOS OS DIAS", "EVERY DAY"):
            return self.tr("freq_every_day")
        elif freq_upper in ("APENAS UMA VEZ", "ONCE ONLY", "ONCE"):
            return self.tr("freq_once")

        # Dicionário mapeando entradas (PT/EN/Siglas) -> Chaves de localização
        mapa_dias = {
            "seg": "day_mon_short", "ter": "day_tue_short", "qua": "day_wed_short",
            "qui": "day_thu_short", "sex": "day_fri_short", "sab": "day_sat_short",
            "sáb": "day_sat_short", "dom": "day_sun_short",
            "segunda-feira": "day_mon_short", "terça-feira": "day_tue_short",
            "quarta-feira": "day_wed_short", "quinta-feira": "day_thu_short",
            "sexta-feira": "day_fri_short", "sábado": "day_sat_short", "domingo": "day_sun_short",
            "mon": "day_mon_short", "tue": "day_tue_short", "wed": "day_wed_short",
            "thu": "day_thu_short", "fri": "day_fri_short", "sat": "day_sat_short", "sun": "day_sun_short"
        }

        # Caso a frequência seja uma lista de dias separados por vírgula
        if "," in freq_str_clean:
            dias = [d.strip().lower() for d in freq_str_clean.split(",")]
            
            if len(dias) == 7:
                return self.tr("freq_every_day")

            dias_traduzidos = []
            for d in dias:
                chave_locale = mapa_dias.get(d)
                if chave_locale:
                    dias_traduzidos.append(self.tr(chave_locale))
                else:
                    dias_traduzidos.append(d.capitalize())
            return ", ".join(dias_traduzidos)

        # Caso seja um dia único em sigla ou texto
        chave_unica = mapa_dias.get(freq_str_clean.lower())
        if chave_unica:
            return self.tr(chave_unica)

        return freq_str_clean

    def atualizar_painel_monitoramento(self):
        for widget in self.container_cards.winfo_children():
            widget.destroy()

        destinos_agendados = {}
        for item in self.agendamentos:
            d_num = item["destino_num"]
            if d_num not in destinos_agendados:
                destinos_agendados[d_num] = []
            destinos_agendados[d_num].append(item)

        if not destinos_agendados:
            lbl_vazio = tk.Label(
                self.container_cards,
                text=self.tr("rt_no_schedules_msg"),
                font=("Arial", 13, "italic"),
                fg="#888888",
                bg="#141414",
                pady=20,
            )
            lbl_vazio.pack()
            return

        col = 0
        row = 0
        hoje_str = time.strftime("%Y-%m-%d")

        for d_num, agendados in destinos_agendados.items():
            nome_dest = self.destinos_nomes[d_num - 1]
            prefixo_dest = self.tr("rt_destination_prefix")
            
            card = tk.LabelFrame(
                self.container_cards,
                text=f" {prefixo_dest} [{d_num:02d}] {nome_dest} ",
                font=("Arial", 12, "bold"),
                fg="#00E5FF",
                bg="#2B2B2B",
                bd=0,
                padx=12,
                pady=12,
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self._bind_mousewheel_area(card)

            for a in agendados:
                foi_hoje = a["ultimo_dia_executado"] == hoje_str
                status_color = "#00FF66" if foi_hoje else "#FFCC00"
                status_txt = self.tr("rt_status_executed") if foi_hoje else self.tr("rt_status_waiting")

                freq_exibicao = self._formatar_frequencia_exibicao(a['frequencia'])

                txt_evento = f"• [{freq_exibicao}] {a['horario']} -> [{a['origem_num']:02d}] {a['origem_nome']} ({status_txt})"
                lbl_ev = tk.Label(
                    card,
                    text=txt_evento,
                    font=("Arial", 11, "bold"),
                    fg=status_color,
                    bg="#2B2B2B",
                    anchor="w",
                )
                lbl_ev.pack(fill="x", pady=2)
                self._bind_mousewheel_area(lbl_ev)

            col += 1
            if col > 2:
                col = 0
                row += 1

    def criar_aba_logs(self):
        """Cria e conecta a caixa de logs na interface de maneira segura."""
        frame_logs = tk.Frame(self.tab_logs, bg="#141414")
        frame_logs.pack(expand=True, fill="both", padx=20, pady=15)

        self.txt_logs = tk.Text(
            frame_logs,
            bg="#0F0F0F",
            fg="#00FF66",
            font=("Consolas", 12),
            bd=0,
            highlightthickness=1,
            highlightbackground="#333333"
        )
        scrollbar_log = ttk.Scrollbar(
            frame_logs, orient="vertical", command=self.txt_logs.yview
        )
        self.txt_logs.configure(yscrollcommand=scrollbar_log.set)

        self.txt_logs.pack(side="left", expand=True, fill="both")
        scrollbar_log.pack(side="right", fill="y")

        gui_handler = GuiLogHandler(self.txt_logs)
        gui_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        gui_handler.setFormatter(gui_formatter)
        logging.getLogger().addHandler(gui_handler)

    def _recriar_interface_apos_edicao(self):
        self.salvar_labels()
        self.atualizar_listas_combobox()
        self.atualizar_tabela_e_agendamentos()
        self.atualizar_painel_monitoramento()

    def atualizar_tabela_e_agendamentos(self):
        if hasattr(self, "tree") and self.tree:
            self.tree.tag_configure("fonte_tabela", font=("Arial", 11, "bold"))

        mapa_status = {
            "AGUARDANDO HORÁRIO": "status_waiting_time",
            "EXECUTADO": "status_executed",
            "DESATIVADO": "status_disabled",
            "CONCLUÍDO (ÚNICO)": "status_executed"
        }

        # Dicionário de frequência cobrindo textos inteiros e siglas de 3 letras
        mapa_freq = {
            "TODOS OS DIAS": "freq_everyday",
            "EVERY DAY": "freq_everyday",
            "APENAS UMA VEZ": "freq_once",
            "ONCE ONLY": "freq_once",
            # Nomes de dias por extenso
            "SEGUNDA-FEIRA": "day_monday",
            "TERÇA-FEIRA": "day_tuesday",
            "QUARTA-FEIRA": "day_wednesday",
            "QUINTA-FEIRA": "day_thursday",
            "SEXTA-FEIRA": "day_friday",
            "SÁBADO": "day_saturday",
            "DOMINGO": "day_sunday",
            # Siglas dos dias
            "SEG": "day_mon_short",
            "TER": "day_tue_short",
            "QUA": "day_wed_short",
            "QUI": "day_thu_short",
            "SEX": "day_fri_short",
            "SAB": "day_sat_short",
            "SÁB": "day_sat_short",
            "DOM": "day_sun_short"
        }

        # ✅ Atualização dos nomes de destino e origem nos agendamentos (compatível com Dicionário e Lista)
        for item in self.agendamentos:
            d_num = item["destino_num"]
            if isinstance(getattr(self, "destinos_nomes", None), dict):
                item["destino_nome"] = self.destinos_nomes.get(
                    d_num, f"{self.tr('label_destination')} {d_num:02d}"
                )
            else:
                d_idx = d_num - 1
                if 0 <= d_idx < len(self.destinos_nomes):
                    item["destino_nome"] = self.destinos_nomes[d_idx]
                else:
                    item["destino_nome"] = f"{self.tr('label_destination')} {d_num:02d}"

            o_num = item["origem_num"]
            if isinstance(getattr(self, "origens_nomes", None), dict):
                item["origem_nome"] = self.origens_nomes.get(
                    o_num, f"{self.tr('label_source')} {o_num:02d}"
                )
            else:
                o_idx = o_num - 1
                if 0 <= o_idx < len(self.origens_nomes):
                    item["origem_nome"] = self.origens_nomes[o_idx]
                else:
                    item["origem_nome"] = f"{self.tr('label_source')} {o_num:02d}"

        # Limpa elementos antigos da Treeview
        for child in self.tree.get_children():
            self.tree.delete(child)

        # Popula a Treeview com os dados atualizados
        for item in self.agendamentos:
            if "uuid" not in item or not item["uuid"]:
                item["uuid"] = str(uuid.uuid4())

            d_num = item["destino_num"]
            o_num = item["origem_num"]

            status_chave = "status_waiting_time"
            if item.get("tipo") == "unico" and item.get("ultimo_dia_executado"):
                status_chave = "status_executed"

            status_traduzido = self.tr(status_chave)
            freq_raw = str(item.get("frequencia", "")).upper().strip()
            
            # Trata frequências compostas por vírgula ("QUA, QUI, SEX, SAB, DOM")
            if "," in freq_raw:
                dias = [d.strip() for d in freq_raw.split(",")]
                if len(dias) == 7:
                    frequencia_traduzida = self.tr("freq_everyday")
                else:
                    dias_traduzidos = [self.tr(mapa_freq.get(d, d)) for d in dias]
                    frequencia_traduzida = ", ".join(dias_traduzidos)
            else:
                chave_freq = mapa_freq.get(freq_raw)
                frequencia_traduzida = self.tr(chave_freq) if chave_freq else freq_raw

            destino_str = f"[{d_num:02d}] {item['destino_nome']}".upper()
            origem_str = f"[{o_num:02d}] {item['origem_nome']}".upper()
            frequencia_str = frequencia_traduzida.upper()
            status_str = status_traduzido.upper()

            self.tree.insert(
                "",
                "end",
                iid=item["uuid"],
                values=(
                    item["id"],
                    destino_str,
                    origem_str,
                    frequencia_str,
                    item["horario"],
                    status_str,
                ),
                tags=("fonte_tabela",)
            )

        if hasattr(self, "footer_label") and self.footer_label:
            self.footer_label.config(text=self.tr("footer_engineering_team"))

    def _criar_lista_gerenciador_64(self, frame_pai, lista_dados, tipo):
        # Localização dinâmica do título da lista
        lbl_tipo = self.tr("label_destination") if tipo.lower().startswith("dest") else self.tr("label_source")
        txt_titulo = self.tr("lbl_list_64_pattern", tipo=lbl_tipo) if hasattr(self, "tr") else f"Lista de {tipo}s (1 a 64):"

        lbl = tk.Label(
            frame_pai,
            text=txt_titulo,
            bg="#2B2B2B",
            fg="#FFFFFF",
            font=("Arial", 11, "bold")
        )
        lbl.pack(anchor="w")

        frame_top_search = tk.Frame(frame_pai, bg="#2B2B2B")
        frame_top_search.pack(fill="x", pady=5)

        tk.Label(
            frame_top_search,
            text=self.tr("lbl_filter"),
            bg="#2B2B2B",
            fg="#A0A0A0",
            font=("Arial", 11)
        ).pack(side="left", padx=(0, 5))

        entry_filtro = tk.Entry(
            frame_top_search,
            bg="#1E1E1E",
            fg="#00E5FF",
            font=("Arial", 12),
            bd=0,
            highlightthickness=1,
            highlightbackground="#444444",
            insertbackground="#FFFFFF"
        )
        entry_filtro.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_editar = HoverButton(
            frame_top_search,
            text=self.tr("btn_edit_label"),
            bg_normal="#00E5FF",
            bg_hover="#33EBFB",
            fg_normal="#000000",
            fg_hover="#000000",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=3
        )
        btn_editar.pack(side="right")

        frame_list = tk.Frame(frame_pai, bg="#2B2B2B")
        frame_list.pack(fill="both", expand=True, pady=5)

        listbox = tk.Listbox(
            frame_list,
            bg="#1E1E1E",
            fg="#FFFFFF",
            bd=0,
            activestyle="none",
            highlightthickness=0,
            selectbackground="#00E5FF",
            selectforeground="#000000",
            font=("Consolas", 12),
            exportselection=False
        )
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)

        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        mapeamento_indices = list(range(64))

        def popular_listbox(termo_busca=""):
            listbox.delete(0, tk.END)
            mapeamento_indices.clear()
            termo = termo_busca.lower().strip()

            for i in range(1, 65):
                nome = lista_dados.get(i, f"Porta {i}")
                string_exibicao = f"[{i:02d}] {nome}"

                if not termo or termo in string_exibicao.lower():
                    listbox.insert(tk.END, string_exibicao)
                    mapeamento_indices.append(i)

        popular_listbox()

        def ao_digitar_filtro(event):
            self.after(10, lambda: popular_listbox(entry_filtro.get()))

        entry_filtro.bind("<KeyRelease>", ao_digitar_filtro)

        def abrir_janela_edicao():
            selecao = listbox.curselection()
            if not selecao:
                tipo_str = self.tr("label_destination") if tipo.lower() in ("destino", "destination") else self.tr("label_source")
                msg_aviso = f"{self.tr('msg_select_item_edit')} ({tipo_str})"
                messagebox.showwarning(self.tr("msg_select_item_title"), msg_aviso)
                return

            idx_filtrado = selecao[0]
            idx_real = mapeamento_indices[idx_filtrado]
            num_porta = idx_real + 1
            nome_atual = lista_dados[idx_real]

            # Define o título conforme o tipo (Destino / Origem)
            if tipo.lower() in ("destino", "destination"):
                titulo_tipo = self.tr("label_destination")
            else:
                titulo_tipo = self.tr("label_source")

            pop = tk.Toplevel(self)
            pop.title(f"{self.tr('btn_edit_selected')} - {titulo_tipo} [{num_porta:02d}]")
            pop.configure(bg="#1E1E1E")
            pop.geometry("380x150")
            pop.resizable(False, False)
            pop.transient(self)
            pop.grab_set()

            pop.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() // 2) - (380 // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (150 // 2)
            pop.geometry(f"+{x}+{y}")

            tk.Label(
                pop,
                text=f"{self.tr('btn_edit_selected')} {titulo_tipo} [{num_porta:02d}]:",
                font=("Arial", 12, "bold"),
                fg="#00E5FF",
                bg="#1E1E1E"
            ).pack(pady=(15, 5))

            entry_novo_nome = tk.Entry(
                pop,
                font=("Arial", 12),
                bg="#2B2B2B",
                fg="#FFFFFF",
                insertbackground="#FFFFFF",
                bd=0,
                highlightthickness=1,
                highlightbackground="#444444",
                width=35
            )
            entry_novo_nome.pack(pady=5, padx=20)
            entry_novo_nome.insert(0, nome_atual)
            entry_novo_nome.select_range(0, tk.END)
            entry_novo_nome.focus_set()

            def confirmar():
                novo_nome = entry_novo_nome.get().strip()
                if novo_nome.startswith("[") and "]" in novo_nome:
                    novo_nome = novo_nome.split("]", 1)[1].strip()

                if not novo_nome:
                    novo_nome = f"{titulo_tipo} {num_porta:02d}"

                lista_dados[idx_real] = novo_nome
                
                # Log formatado
                logging.info(f"CONFIG: {titulo_tipo} [{num_porta:02d}] -> '{novo_nome}'")

                popular_listbox(entry_filtro.get())
                self._recriar_interface_apos_edicao()
                
                pop.destroy()

            btn_confirmar = HoverButton(
                pop,
                text=self.tr("btn_save_changes"),
                bg_normal="#00E5FF",
                bg_hover="#33EBFB",
                fg_normal="#000000",
                fg_hover="#000000",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=4,
                command=confirmar
            )
            btn_confirmar.pack(pady=10)

            entry_novo_nome.bind("<Return>", lambda e: confirmar())

        btn_editar.config(command=abrir_janela_edicao)
        listbox.bind("<Double-Button-1>", lambda e: abrir_janela_edicao())
        listbox.bind("<Return>", lambda e: abrir_janela_edicao())

    def salvar_configuracao_ip(self):
        novo_ip = self.entry_ip.get().strip()
        padrao_ip = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

        if not re.match(padrao_ip, novo_ip):
            messagebox.showerror(
                self.tr("msg_invalid_ip_title"),
                self.tr("msg_invalid_ip_text"),
            )
            return

        ip_anterior = self.ip_matriz
        self.ip_matriz = novo_ip
        self.lbl_status_ip.config(text=f"{self.tr('lbl_current_ip')} {self.ip_matriz}")

        log_msg = self.tr("log_ip_changed").format(old=ip_anterior, new=self.ip_matriz)
        logging.info(log_msg)

        msg_sucesso = f"{self.tr('msg_ip_updated_success')}\n{self.tr('lbl_current_ip')} {self.ip_matriz}"
        messagebox.showinfo(
            self.tr("msg_success_title"), msg_sucesso
        )

    def loop_agendador(self):
        while self.agendador_ativo:
            agora_hora = time.strftime("%H:%M:%S")
            hoje_data = time.strftime("%Y-%m-%d")
            dia_semana_hoje = MAP_DIAS_INDEX[time.localtime().tm_wday]

            for item in list(self.agendamentos):
                tipo_agendamento = item.get("tipo", "recorrente")
                nao_executado_hoje = item.get("ultimo_dia_executado", "") != hoje_data

                frequencia_valida = False

                if tipo_agendamento == "unico":
                    data_evento = item.get("data_unica", "")
                    if data_evento == hoje_data and item.get("ultimo_dia_executado", "") != hoje_data:
                        frequencia_valida = True
                else:
                    frequencia_valida = dia_semana_hoje in item.get("dias_lista", [])

                if frequencia_valida and nao_executado_hoje and item["horario"] == agora_hora:
                    item["ultimo_dia_executado"] = hoje_data
                    self.salvar_agendamentos()
                    
                    str_acao_auto = self.tr("log_scheduled_auto")
                    self.comutar_input(
                        item_id=item["id"],
                        posicao_destino=item["destino_num"],
                        entrada_origem=item["origem_num"],
                        nome_destino=item["destino_nome"],
                        nome_origem=item["origem_nome"],
                        origem_acao=str_acao_auto,
                        tipo_agendamento=tipo_agendamento
                    )

            time.sleep(0.8)

    def atualizar_status_tree(self, item_id, novo_status):
        try:
            for child in self.tree.get_children():
                values = self.tree.item(child, "values")
                if int(values[0]) == item_id:
                    self.tree.item(
                        child,
                        values=(
                            values[0],
                            values[1],
                            values[2],
                            values[3],
                            values[4],
                            novo_status,
                        ),
                    )
        except Exception as e:
            logging.error(f"Erro ao atualizar status na Treeview: {e}")

    def comutar_input(
        self,
        item_id,
        posicao_destino,
        entrada_origem,
        nome_destino="",
        nome_origem="",
        origem_acao="SISTEMA",
        tipo_agendamento="recorrente"
    ):
        url = f"http://{self.ip_matriz}/config"
        headers = {
            "Accept": "*/*",
            "Referer": f"http://{self.ip_matriz}/index.tmpl",
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
        }
        cookies = {"session": "invalid"}

        def safe_after(ms, func):
            try:
                self.after(ms, func)
            except Exception:
                pass

        def worker():
            params_get = {
                "action": "get",
                "configid": "0",
                "paramid": f"eParamID_XPT_Destination{posicao_destino}_Status",
            }
            
            origem_anterior_str = self.tr("status_unknown")
            try:
                res_get = requests.get(url, params=params_get, headers=headers, cookies=cookies, timeout=2.5)
                if res_get.status_code == 200:
                    match = re.search(r'"value"\s*:\s*"(\d+)"', res_get.text)
                    if match:
                        orig_prev_num = int(match.group(1))
                        
                        # Ajustado para dicionários indexados de 1 a 64
                        nome_prev = (
                            self.origens_nomes.get(orig_prev_num)
                            if isinstance(getattr(self, "origens_nomes", None), dict)
                            else self.origens_nomes[orig_prev_num - 1]
                            if hasattr(self, "origens_nomes") and 0 < orig_prev_num <= len(self.origens_nomes)
                            else f"{self.tr('label_source')} {orig_prev_num:02d}"
                        )
                        origem_anterior_str = f"[{orig_prev_num:02d}] {nome_prev}"
            except Exception as e:
                msg_log = self.tr("log_status_check_failed").format(dest=posicao_destino, err=e)
                logging.warning(msg_log)

            params_set = {
                "action": "set",
                "configid": "0",
                "paramid": f"eParamID_XPT_Destination{posicao_destino}_Status",
                "value": str(entrada_origem),
            }

            try:
                response = requests.get(
                    url,
                    params=params_set,
                    headers=headers,
                    cookies=cookies,
                    timeout=2.5,
                )

                if response.status_code == 200:
                    st_txt = (
                        self.tr("status_done_manual")
                        if "MANUAL" in origem_acao.upper() or "FORC" in origem_acao.upper()
                        else self.tr("status_done_today")
                    )
                    safe_after(0, lambda: self.atualizar_status_tree(item_id, st_txt))
                    safe_after(0, self.atualizar_painel_monitoramento)

                    log_str = (
                        f"[{origem_acao}] KUMO -> {self.tr('label_destination')} [{posicao_destino:02d}] {nome_destino} | "
                        f"{self.tr('log_previous_state')}: {origem_anterior_str} -> {self.tr('log_new_state')}: [{entrada_origem:02d}] {nome_origem}"
                    )
                    logging.info(log_str)

                    if tipo_agendamento == "unico":
                        safe_after(0, lambda: self.remover_agendamento(item_id))
                else:
                    # ✅ TRADUZIDO: Usando chaves do locales.py
                    err_msg = self.tr("err_http_switch").format(
                        code=response.status_code, 
                        dest=posicao_destino, 
                        ip=self.ip_matriz
                    )
                    logging.error(err_msg)
                    safe_after(0, lambda: self.atualizar_status_tree(item_id, self.tr("status_server_error")))
                    safe_after(0, lambda: messagebox.showerror(self.tr("msg_matrix_failure"), err_msg))

            except requests.exceptions.RequestException as req_err:
                # ✅ TRADUZIDO: Usando chaves do locales.py
                err_msg = self.tr("err_connection_switch").format(
                    ip=self.ip_matriz, 
                    err=req_err
                )
                logging.error(err_msg)
                safe_after(0, lambda: self.atualizar_status_tree(item_id, self.tr("status_connection_error")))
                safe_after(0, lambda: messagebox.showerror(
                    self.tr("msg_connection_alert_title"), 
                    f"{self.tr('msg_connection_alert_text')}: {self.ip_matriz}\n\n{self.tr('msg_check_cable')}"
                ))

        threading.Thread(target=worker, daemon=True).start()
        
if __name__ == "__main__":
    # 0. Define o ícone global para TODAS as janelas (Popups e Principal)
    definir_icone_padrao_global("logo.ico")  # Ajuste o nome do arquivo se necessário

    # 1. Obtém o idioma selecionado
    idioma_definido = obter_ou_perguntar_idioma()

    # 2. Configura a instância estática de tradução PRIMEIRO
    I18n.set_language(idioma_definido)

    # 3. Obtém ou pergunta o IP da Matriz (já traduzido para o idioma escolhido)
    ip_matriz_definido = obter_ou_perguntar_ip_matriz()

    # 4. Inicializa a aplicação principal com o IP definido (ou o default caso tenha fechado a popup)
    app = AgendadorKumo64x64(idioma_atual=idioma_definido, ip_matriz=ip_matriz_definido)

    app.footer_label = tk.Label(
        app,
        text=app.tr("footer_engineering_team"),
        font=("Helvetica", 10),
        bg="#141414",
        fg="#666666",
    )
    app.footer_label.pack(side="bottom", fill="x", pady=(0, 5))

    app.mainloop()