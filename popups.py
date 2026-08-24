# ==============================================================================
# COPYRIGHT (C) 2026 SISTEMA JORNAL DO COMMERCIO LTDA
# TODOS OS DIREITOS RESERVADOS.
#
# Autor: Gabriel Menge
# Aplicação: Popups para AjaSchedule - Versão 1.05 (Suporte Multi-Idioma)
# ==============================================================================

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class BasePopup(tk.Toplevel):
    def __init__(self, parent, titulo, largura=400, altura=500, callback_cancelar=None):
        super().__init__(parent)
        self.master = parent
        self.title(titulo)
        self.geometry(f"{largura}x{altura}")
        self.configure(bg="#1E1E1E")
        self.resizable(False, False)
        
        self.callback_cancelar = callback_cancelar

        # Bloqueio de segurança (Debounce) ao abrir o popup (250ms)
        self.bloqueado_por_debounce = True
        self.after(250, self._desbloquear_clique)

        self.transient(parent)
        self.grab_set()

        # Centraliza a janela popup em relação à janela principal
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (largura // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (altura // 2)
        self.geometry(f"+{x}+{y}")

        # Foco inicial sem travar a destruição da janela
        self.lift()
        self.focus_set()

        # Captura o fechar no X da janela e no ESC
        self.protocol("WM_DELETE_WINDOW", self.fechar_cancelar)
        self.bind("<Escape>", lambda event: self.fechar_cancelar())

    def _desbloquear_clique(self):
        self.bloqueado_por_debounce = False

    def fechar_cancelar(self):
        """Executa o callback de cancelamento (se existir) e destrói a janela."""
        if self.callback_cancelar:
            self.callback_cancelar()
        self.destroy()


class SeletorCanalPopup(BasePopup):
    def __init__(self, parent, tipo_nome, lista_opcoes, callback_confirmar, callback_cancelar=None, valor_inicial=None):
        # Mapeamento para busca de chaves de internacionalização
        mapa_titulos = {
            "destino": ("title_select_destination", "header_select_destination"),
            "origem": ("title_select_source", "header_select_source"),
            "hora": ("title_select_hour", "header_select_hour"),
            "minuto": ("title_select_minute", "header_select_minute"),
        }

        if tipo_nome in mapa_titulos:
            key_title, key_header = mapa_titulos[tipo_nome]
            titulo_janela = parent.tr(key_title)
            texto_cabecalho = parent.tr(key_header)
        else:
            titulo_janela = tipo_nome
            texto_cabecalho = tipo_nome.upper()

        super().__init__(parent, titulo_janela, largura=420, altura=520, callback_cancelar=callback_cancelar)
        
        self.lista_completa = lista_opcoes
        self.callback_confirmar = callback_confirmar
        self.itens_filtrados = list(lista_opcoes)
        
        # Variável para rastrear o temporizador do Auto-Next
        self._auto_select_timer = None

        # Cabeçalho
        tk.Label(
            self,
            text=texto_cabecalho,
            font=("Arial", 11, "bold"),
            fg="#00E5FF",
            bg="#1E1E1E"
        ).pack(pady=(12, 5))

        # Campo de Busca
        frame_busca = tk.Frame(self, bg="#1E1E1E")
        frame_busca.pack(fill="x", padx=15, pady=5)

        tk.Label(
            frame_busca, text=parent.tr("lbl_filter"), font=("Arial", 11, "bold"), fg="#A0A0A0", bg="#1E1E1E"
        ).pack(side="left", padx=(0, 5))

        self.entry_busca = tk.Entry(
            frame_busca,
            font=("Arial", 12),
            bg="#2B2B2B",
            fg="#00E5FF",
            insertbackground="#FFFFFF",
            bd=0,
            highlightthickness=1,
            highlightbackground="#444444"
        )
        self.entry_busca.pack(side="left", fill="x", expand=True)
        self.entry_busca.bind("<KeyRelease>", self.filtrar_lista)
        
        # Binds de navegação direta via teclado
        self.entry_busca.bind("<Down>", self._navegar_lista)
        self.entry_busca.bind("<Up>", self._navegar_lista)

        # Listbox e Scrollbar
        frame_lista = tk.Frame(self, bg="#1E1E1E")
        frame_lista.pack(fill="both", expand=True, padx=15, pady=5)

        self.listbox = tk.Listbox(
            frame_lista,
            font=("Consolas", 12),
            bg="#2B2B2B",
            fg="#FFFFFF",
            selectbackground="#00E5FF",
            selectforeground="#000000",
            bd=0,
            activestyle="none",
            highlightthickness=0
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Eventos de Seleção
        self.listbox.bind("<ButtonRelease-1>", self._on_listbox_single_click)
        self.listbox.bind("<Double-Button-1>", lambda e: self.confirmar_selecao())
        self.listbox.bind("<Return>", lambda e: self.confirmar_selecao())
        self.entry_busca.bind("<Return>", lambda e: self.confirmar_selecao())

        self.popular_listbox()

        # Seleciona e foca o item correspondente
        if valor_inicial and valor_inicial in self.lista_completa:
            idx = self.lista_completa.index(valor_inicial)
            self.listbox.selection_set(idx)
            self.listbox.see(idx)

        self.entry_busca.focus_set()

    def popular_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.itens_filtrados:
            self.listbox.insert(tk.END, item)

    def _cancelar_timer(self):
        if self._auto_select_timer is not None:
            self.after_cancel(self._auto_select_timer)
            self._auto_select_timer = None
        self.entry_busca.config(highlightbackground="#444444")

    def _on_listbox_single_click(self, event=None):
        if self.bloqueado_por_debounce:
            return

        self._cancelar_timer()
        
        if event:
            index_clicado = self.listbox.nearest(event.y)
            if index_clicado >= 0 and index_clicado < len(self.itens_filtrados):
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(index_clicado)
                self.confirmar_selecao()

    def _navegar_lista(self, event):
        if not self.itens_filtrados:
            return

        self._cancelar_timer()
        selecao = self.listbox.curselection()
        idx = selecao[0] if selecao else 0

        if event.keysym == "Down":
            idx = min(idx + 1, len(self.itens_filtrados) - 1)
        elif event.keysym == "Up":
            idx = max(idx - 1, 0)

        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.listbox.see(idx)
        return "break"

    def filtrar_lista(self, event=None):
        if event and event.keysym in ("Down", "Up", "Return", "Escape", "Tab"):
            return

        self._cancelar_timer()

        termo = self.entry_busca.get().strip().lower()
        if not termo:
            self.itens_filtrados = list(self.lista_completa)
        else:
            self.itens_filtrados = [
                item for item in self.lista_completa if termo in item.lower()
            ]
        self.popular_listbox()
        
        if self.itens_filtrados:
            self.listbox.selection_set(0)

        # LÓGICA DE AUTO-NEXT DINÂMICO
        termo_raw = self.entry_busca.get().strip()
        if termo_raw.isdigit():
            num_str = f"{int(termo_raw):02d}"
            target_bracket = f"[{num_str}]"
            target_space = f"{num_str} "
            
            match_index = -1
            for i, item in enumerate(self.itens_filtrados):
                if item.startswith(target_bracket) or item.startswith(target_space):
                    match_index = i
                    break
            
            if match_index != -1:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(match_index)
                self.listbox.see(match_index)
                
                self.entry_busca.config(highlightbackground="#00FF66")

                delay = 450 if len(termo_raw) >= 2 else 800
                self._auto_select_timer = self.after(delay, self.confirmar_selecao)

    def confirmar_selecao(self):
        if self.bloqueado_por_debounce:
            return
        
        self._cancelar_timer()

        selecao = self.listbox.curselection()
        if selecao:
            valor = self.itens_filtrados[selecao[0]]
            self.destroy()
            self.callback_confirmar(valor)
        elif self.itens_filtrados:
            valor = self.itens_filtrados[0]
            self.destroy()
            self.callback_confirmar(valor)


class SeletorDiasPopup(BasePopup):
    def __init__(self, parent, config_frequencia_atual, callback_confirmar, callback_cancelar=None):
        super().__init__(
            parent,
            parent.tr("title_freq_popup"),
            largura=420,
            altura=440,
            callback_cancelar=callback_cancelar
        )

        self.callback_confirmar = callback_confirmar
        
        # Mapeamento do identificador do dia no backend para a chave do locales.py
        self.dias_mapeamento = [
            ("seg", "day_monday"),
            ("ter", "day_tuesday"),
            ("qua", "day_wednesday"),
            ("qui", "day_thursday"),
            ("sex", "day_friday"),
            ("sab", "day_saturday"),
            ("dom", "day_sunday")
        ]

        # Extrai o estado atual recebido do formulário exatamente como ele vem
        if isinstance(config_frequencia_atual, dict):
            self.tipo_frequencia = config_frequencia_atual.get("tipo", "recorrente")
            self.dias_selecionados = list(config_frequencia_atual.get("dias", []))
            self.data_unica = config_frequencia_atual.get("data", datetime.now().strftime("%Y-%m-%d"))
        else:
            self.tipo_frequencia = "recorrente"
            self.dias_selecionados = list(config_frequencia_atual) if isinstance(config_frequencia_atual, list) else []
            self.data_unica = datetime.now().strftime("%Y-%m-%d")

        tk.Label(
            self,
            text=parent.tr("header_freq_routine"),
            font=("Arial", 13, "bold"),
            fg="#00E5FF",
            bg="#1E1E1E"
        ).pack(pady=(12, 5))

        # Modos (Recorrente vs Evento Único)
        frame_tipo = tk.Frame(self, bg="#1E1E1E")
        frame_tipo.pack(fill="x", padx=20, pady=5)

        self.var_tipo = tk.StringVar(value=self.tipo_frequencia)

        rb_rec = tk.Radiobutton(
            frame_tipo, text=parent.tr("radio_recurring_days"), variable=self.var_tipo, value="recorrente",
            bg="#1E1E1E", fg="#FFFFFF", selectcolor="#2B2B2B", activebackground="#1E1E1E",
            activeforeground="#00E5FF", font=("Arial", 11, "bold"), command=self.alternar_modo
        )
        rb_rec.pack(side="left", padx=10)

        rb_uni = tk.Radiobutton(
            frame_tipo, text=parent.tr("radio_single_date"), variable=self.var_tipo, value="unico",
            bg="#1E1E1E", fg="#FFFFFF", selectcolor="#2B2B2B", activebackground="#1E1E1E",
            activeforeground="#00E5FF", font=("Arial", 11, "bold"), command=self.alternar_modo
        )
        rb_uni.pack(side="left", padx=10)

        # Container Central de Conteúdo
        self.frame_conteudo = tk.Frame(self, bg="#1E1E1E")
        self.frame_conteudo.pack(fill="both", expand=True, padx=20, pady=5)

        # Container dos Dias
        self.frame_dias = tk.Frame(self.frame_conteudo, bg="#1E1E1E")
        self.vars_dias = {}

        mapeamento_alias = {
            "seg": ["seg", "mon", "monday", "segunda"],
            "ter": ["ter", "tue", "tuesday", "terça", "terca"],
            "qua": ["qua", "wed", "wednesday", "quarta"],
            "qui": ["qui", "thu", "thursday", "quinta"],
            "sex": ["sex", "fri", "friday", "sexta"],
            "sab": ["sab", "sat", "saturday", "sábado", "sabado"],
            "dom": ["dom", "sun", "sunday", "domingo"]
        }

        dias_sel_lower = [str(d).lower() for d in self.dias_selecionados]

        for cod_dia, key_locale in self.dias_mapeamento:
            nome_traduzido = parent.tr(key_locale)
            aliases = mapeamento_alias.get(cod_dia, [cod_dia])
            
            # Se a lista enviada for vazia [], marcado será False para todos os dias
            marcado = any(
                any(alias in dia_salvo for alias in aliases)
                for dia_salvo in dias_sel_lower
            )

            var = tk.BooleanVar(value=marcado)
            self.vars_dias[cod_dia] = var
            
            cb = tk.Checkbutton(
                self.frame_dias, text=nome_traduzido, variable=var, bg="#1E1E1E", fg="#FFFFFF",
                selectcolor="#2B2B2B", activebackground="#1E1E1E", activeforeground="#00E5FF",
                font=("Arial", 11)
            )
            cb.pack(anchor="w", padx=30, pady=1)
            cb.bind("<Return>", lambda e: self.confirmar())

        # Container da Data Única
        self.frame_data = tk.Frame(self.frame_conteudo, bg="#1E1E1E")
        tk.Label(
            self.frame_data, text=parent.tr("lbl_event_date"),
            font=("Arial", 11, "bold"), fg="#A0A0A0", bg="#1E1E1E"
        ).pack(pady=(15, 2))

        self.entry_data = tk.Entry(
            self.frame_data, font=("Arial", 11), bg="#2B2B2B", fg="#00E5FF",
            insertbackground="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#444444", width=15,
            justify="center"
        )
        self.entry_data.pack(pady=5)
        self.entry_data.insert(0, self.data_unica)
        self.entry_data.bind("<Return>", lambda e: self.confirmar())

        # Frame Inferior do Botão
        frame_rodape = tk.Frame(self, bg="#1E1E1E")
        frame_rodape.pack(fill="x", side="bottom", pady=15)

        self.btn_confirmar = tk.Button(
            frame_rodape, text=parent.tr("btn_confirm_freq"), bg="#00E5FF", fg="#000000",
            activebackground="#33EBFB", activeforeground="#000000",
            font=("Arial", 11, "bold"), bd=0, padx=20, pady=8, command=self.confirmar
        )
        self.btn_confirmar.pack()

        self.bind("<Return>", lambda event: self.confirmar())
        rb_rec.bind("<Return>", lambda event: self.confirmar())
        rb_uni.bind("<Return>", lambda event: self.confirmar())

        self.alternar_modo()

    def alternar_modo(self):
        modo = self.var_tipo.get()
        if modo == "recorrente":
            self.frame_data.pack_forget()
            self.frame_dias.pack(fill="both", expand=True)
            self.btn_confirmar.focus_set()
        else:
            self.frame_dias.pack_forget()
            self.frame_data.pack(fill="both", expand=True)
            self.entry_data.focus_set()
            self.entry_data.select_range(0, tk.END)

    def confirmar(self):
        if getattr(self, "bloqueado_por_debounce", False):
            return

        modo = self.var_tipo.get()
        if modo == "recorrente":
            dias_escolhidos = [cod_dia for cod_dia, var in self.vars_dias.items() if var.get()]
            config = {"tipo": "recorrente", "dias": dias_escolhidos}
        else:
            config = {"tipo": "unico", "data": self.entry_data.get().strip()}

        self.destroy()
        self.callback_confirmar(config)