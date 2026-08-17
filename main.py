import os
import textwrap
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import requests as rq
import urllib3
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.use("Agg")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
RESULTS_DIR = "results"

FILES = {
    "EXP_2022.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2022.csv",
    "EXP_2023.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2023.csv",
    "EXP_2024.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2024.csv",
    "EXP_2025.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2025.csv",
    "EXP_2026.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2026.csv",
    "IMP_2022.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2022.csv",
    "IMP_2023.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2023.csv",
    "IMP_2024.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2024.csv",
    "IMP_2025.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2025.csv",
    "IMP_2026.csv": "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2026.csv",
    "NCM.csv": "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM.csv",
    "PAIS.csv": "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv",
}

OPERATION_PREFIX = {"Export": "EXP", "Import": "IMP"}

# Download files
def download_files(log_callback=print):
    os.makedirs(RAW_DIR, exist_ok=True)
    for filename, url in FILES.items():
        filepath = os.path.join(RAW_DIR, filename)
        if os.path.exists(filepath):
            log_callback(f"{filename} ja baixado.")
            continue
        log_callback(f"Baixando {filename}...")
        response = rq.get(url, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        log_callback(f"{filename} baixado com sucesso.")

# Cleaning data
def process_dataset(prefix, year, log_callback=print):
    output_path = os.path.join(PROCESSED_DIR, f"{prefix}_{year}.csv")
    if os.path.exists(output_path):
        log_callback(f"{prefix}_{year}.csv ja processado.")
        return

    df = pd.read_csv(os.path.join(RAW_DIR, f"{prefix}_{year}.csv"), sep=";")
    df = df.drop(
        columns=["CO_UNID", "SG_UF_NCM", "CO_URF", "CO_VIA", "QT_ESTAT", "KG_LIQUIDO"]
    )

    df_country = pd.read_csv(
        os.path.join(RAW_DIR, "PAIS.csv"), sep=";", encoding="latin1"
    )
    df_country = df_country.drop(
        columns=["CO_PAIS_ISON3", "CO_PAIS_ISOA3", "NO_PAIS", "NO_PAIS_ESP"]
    )

    df = df.merge(df_country, on="CO_PAIS", how="left")
    df = df.drop(columns=["CO_PAIS"])

    df_ncm = pd.read_csv(os.path.join(RAW_DIR, "NCM.csv"), sep=";", encoding="latin1")
    df_ncm = df_ncm.drop(
        columns=[
            "CO_UNID",
            "CO_SH6",
            "CO_PPE",
            "CO_PPI",
            "CO_FAT_AGREG",
            "CO_CUCI_ITEM",
            "CO_CGCE_N3",
            "CO_SIIT",
            "CO_ISIC_CLASSE",
            "CO_EXP_SUBSET",
            "NO_NCM_POR",
            "NO_NCM_ESP",
        ]
    )

    df = df.merge(df_ncm, on="CO_NCM", how="left")
    df = df.rename(
        columns={
            "CO_ANO": "Year",
            "CO_MES": "Month",
            "CO_NCM": "NCM",
            "VL_FOB": "Valor USD",
            "NO_PAIS_ING": "Country",
            "NO_NCM_ING": "NCM Description",
        }
    )
    df = df[["Year", "Country", "Month", "Valor USD", "NCM Description", "NCM"]]
    df = df.sort_values("Country")

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(output_path, index=False)
    log_callback(f"{prefix}_{year}.csv salvo e pronto.")

# Process data
def process_all(log_callback=print):
    for prefix in ("EXP", "IMP"):
        for year in ("2022", "2023", "2024", "2025", "2026"):
            process_dataset(prefix, year, log_callback)

# Save processed data
def load_processed(operation, year):
    prefix = OPERATION_PREFIX[operation]
    path = os.path.join(PROCESSED_DIR, f"{prefix}_{year}.csv")
    return pd.read_csv(path)

# Final message
def is_data_ready():
    return all(
        os.path.exists(os.path.join(PROCESSED_DIR, f"{prefix}_{year}.csv"))
        for prefix in ("EXP", "IMP")
        for year in ("2022", "2025")
    )

# Quebra de texto
def wrap_label(text, width=18):
    text = str(text)
    wrapped = textwrap.wrap(text, width=width)
    return "\n".join(wrapped) if wrapped else text

# CUSTOM TKINTER
class ComexStatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ComexBR DataFetcher")
        self.geometry("1100x680")
        self.minsize(950, 620)

        self.df_country = None
        self.current_filename_base = None
        self.current_operation = None
        self.current_year = None
        self.chart_canvas = None
        self.current_figure = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        self._show_page("dados")

    # Sidebar
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=190, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        logo = ctk.CTkLabel(
            sidebar, text="ComexBR", font=ctk.CTkFont(size=20, weight="bold")
        )
        logo.pack(padx=20, pady=(25, 5), anchor="w")

        subtitle = ctk.CTkLabel(
            sidebar, text="DataFetcher", font=ctk.CTkFont(size=13), text_color="gray60"
        )
        subtitle.pack(padx=20, pady=(0, 25), anchor="w")

        self.nav_buttons = {}
        nav_items = [
            ("dados", "Dados"),
            ("pesquisa", "Pesquisa"),
            ("resultados", "Resultados"),
            ("grafico", "Grafico"),
        ]
        for key, label in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=label,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                command=lambda k=key: self._show_page(k),
            )
            btn.pack(padx=15, pady=6, fill="x")
            self.nav_buttons[key] = btn

        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        self.appearance_switch = ctk.CTkSwitch(
            sidebar, text="Dark mode", command=self._toggle_appearance
        )
        self.appearance_switch.pack(padx=20, pady=25, anchor="w")
        self.appearance_switch.select()

    def _toggle_appearance(self):
        mode = "dark" if self.appearance_switch.get() else "light"
        ctk.set_appearance_mode(mode)

    def _highlight_nav(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    # Main Window
    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.pages = {}
        for key, builder in [
            ("dados", self._build_page_dados),
            ("pesquisa", self._build_page_pesquisa),
            ("resultados", self._build_page_resultados),
            ("grafico", self._build_page_grafico),
        ]:
            page = ctk.CTkFrame(self.content, corner_radius=10)
            page.grid(row=0, column=0, sticky="nsew")
            builder(page)
            self.pages[key] = page

    def _show_page(self, key):
        self.pages[key].tkraise()
        self._highlight_nav(key)

    # Data Tab
    def _build_page_dados(self, frame):
        ctk.CTkLabel(
            frame, text="Dados", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(padx=20, pady=(20, 5), anchor="w")

        ctk.CTkLabel(
            frame,
            text="Baixe e processe os dados do ComexStat antes de pesquisar.",
            text_color="gray60",
        ).pack(padx=20, pady=(0, 15), anchor="w")

        self.btn_download = ctk.CTkButton(
            frame, text="Baixar e processar dados", command=self._start_download_thread
        )
        self.btn_download.pack(padx=20, pady=5, anchor="w")

        self.progress_bar = ctk.CTkProgressBar(frame, mode="indeterminate", width=400)
        self.progress_bar.pack(padx=20, pady=10, anchor="w")
        self.progress_bar.set(0)

        self.log_box = ctk.CTkTextbox(frame, height=380)
        self.log_box.pack(padx=20, pady=10, fill="both", expand=True)
        self.log_box.configure(state="disabled")

        if is_data_ready():
            self._log("Dados ja processados e prontos para uso.")

    def _log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _start_download_thread(self):
        self.btn_download.configure(state="disabled", text="Processando...")
        self.progress_bar.start()
        thread = threading.Thread(target=self._download_and_process, daemon=True)
        thread.start()

    def _download_and_process(self):
        try:
            download_files(log_callback=lambda msg: self.after(0, self._log, msg))
            process_all(log_callback=lambda msg: self.after(0, self._log, msg))
            self.after(0, self._log, "\nDados prontos! Va para a pagina Pesquisa.")
        except Exception as exc:
            self.after(0, self._log, f"Erro: {exc}")
            self.after(0, lambda: messagebox.showerror("Erro no download", str(exc)))
        finally:
            self.after(0, self.progress_bar.stop)
            self.after(
                0,
                lambda: self.btn_download.configure(
                    state="normal", text="Baixar e processar dados"
                ),
            )

    # Research Tab
    def _build_page_pesquisa(self, frame):
        ctk.CTkLabel(
            frame, text="Pesquisa", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(padx=20, pady=(20, 15), anchor="w")

        form = ctk.CTkFrame(frame, fg_color="transparent")
        form.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form, text="Operacao:").grid(
            row=0, column=0, padx=(0, 10), pady=10, sticky="w"
        )
        self.operation_menu = ctk.CTkOptionMenu(form, values=["Export", "Import"])
        self.operation_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(form, text="Ano:").grid(
            row=1, column=0, padx=(0, 10), pady=10, sticky="w"
        )
        self.year_menu = ctk.CTkOptionMenu(
            form, values=["2022", "2023", "2024", "2025", "2026"]
        )
        self.year_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(form, text="Pais:").grid(
            row=2, column=0, padx=(0, 10), pady=10, sticky="w"
        )
        self.country_entry = ctk.CTkEntry(
            form, width=250, placeholder_text="Ex: Japan, Germany, Argentina..."
        )
        self.country_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.country_entry.bind("<KeyRelease>", self._on_country_keyrelease)
        self.country_entry.bind(
            "<FocusOut>", lambda e: self.after(150, self._hide_suggestions)
        )
        self.country_entry.bind("<Escape>", lambda e: self._hide_suggestions())

        self.suggestion_window = None
        self._country_list_cache = None

        self.search_button = ctk.CTkButton(
            frame, text="Pesquisar", command=self._run_search
        )
        self.search_button.pack(padx=20, pady=10, anchor="w")

        self.pesquisa_status = ctk.CTkLabel(frame, text="", text_color="orange")
        self.pesquisa_status.pack(padx=20, pady=5, anchor="w")
        self.country_entry.bind("<KeyRelease>", self._on_country_keyrelease)
        self.country_entry.bind(
            "<FocusOut>", lambda e: self.after(150, self._hide_suggestions)
        )
        self.country_entry.bind("<Escape>", lambda e: self._hide_suggestions())

        self.suggestion_window = None
        self._country_list_cache = None

    def _get_country_list(self):
        if self._country_list_cache is not None:
            return self._country_list_cache
    
        path = os.path.join(RAW_DIR, "PAIS.csv")
        if not os.path.exists(path):
            return []
    
        df = pd.read_csv(path, sep=";", encoding="latin1")
        countries = sorted(df["NO_PAIS_ING"].dropna().unique().tolist())
        self._country_list_cache = countries
        return countries

    def _on_country_keyrelease(self, event):
        text = self.country_entry.get().strip()
        if not text:
            self._hide_suggestions()
            return
        countries = self._get_country_list()
        text_lower = text.lower()
        matches = [c for c in countries if c.lower().startswith(text_lower)]
        if not matches:
            matches = [c for c in countries if text_lower in c.lower()]
        matches = matches[:8]
        if not matches:
            self._hide_suggestions()
            return
    
        self._show_suggestions(matches)

    def _show_suggestions(self, matches):
        self._hide_suggestions()
        x = self.country_entry.winfo_rootx()
        y = self.country_entry.winfo_rooty() + self.country_entry.winfo_height()
        width = self.country_entry.winfo_width()
        row_height = 28
    
        self.suggestion_window = ctk.CTkToplevel(self)
        self.suggestion_window.overrideredirect(True)
        self.suggestion_window.geometry(f"{width}x{len(matches) * row_height}+{x}+{y}")
        self.suggestion_window.attributes("-topmost", True)
    
        for country in matches:
            btn = ctk.CTkButton(
                self.suggestion_window,
                text=country,
                anchor="w",
                height=row_height,
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                command=lambda country=country: self._select_country(country),
            )
            btn.pack(fill="x", padx=1, pady=0)

    def _select_country(self, country):
        self.country_entry.delete(0, "end")
        self.country_entry.insert(0, country)
        self._hide_suggestions()
        self.country_entry.focus_set()

    def _hide_suggestions(self):
        if self.suggestion_window is not None:
            self.suggestion_window.destroy()
            self.suggestion_window = None

    def _run_search(self):
        if not is_data_ready():
            messagebox.showwarning(
                "Dados indisponiveis",
                "Baixe e processe os dados na pagina 'Dados' primeiro.",
            )
            return

        operation = self.operation_menu.get()
        year = self.year_menu.get()
        country = self.country_entry.get().strip()

        if not country:
            self.pesquisa_status.configure(text="Digite o nome de um pais.")
            return

        try:
            df = load_processed(operation, year)
        except FileNotFoundError:
            messagebox.showerror(
                "Erro", "Arquivo processado nao encontrado. Refaca o download."
            )
            return

        df_country = df[df["Country"] == country.title()]
        if df_country.empty:
            self.pesquisa_status.configure(text=f"Pais '{country}' nao encontrado.")
            self.df_country = None
            return

        self.pesquisa_status.configure(
            text=f"{len(df_country)} registros encontrados.", text_color="lightgreen"
        )
        self.df_country = df_country
        self.current_filename_base = country.replace("/", "-").replace(" ", "_").title()
        self.current_operation = operation
        self.current_year = year

        self._populate_results_table(df_country)
        self._show_page("resultados")

    # Results Tab
    def _build_page_resultados(self, frame):
        ctk.CTkLabel(
            frame, text="Resultados", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(padx=20, pady=(20, 5), anchor="w")

        self.total_label = ctk.CTkLabel(
            frame, text="Nenhuma pesquisa realizada ainda.", text_color="gray60"
        )
        self.total_label.pack(padx=20, pady=(0, 10), anchor="w")

        table_frame = ctk.CTkFrame(frame)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("Year", "Country", "Month", "Valor USD", "NCM Description", "NCM")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=15
        )
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        save_frame = ctk.CTkFrame(frame, fg_color="transparent")
        save_frame.pack(padx=20, pady=10, anchor="w")
        ctk.CTkLabel(save_frame, text="Salvar tabela como:").pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkButton(
            save_frame, text="CSV", width=80, command=lambda: self._save_table("csv")
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            save_frame, text="Excel", width=80, command=lambda: self._save_table("xlsx")
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            save_frame, text="JSON", width=80, command=lambda: self._save_table("json")
        ).pack(side="left", padx=5)

    def _populate_results_table(self, df_country):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in df_country.iterrows():
            self.tree.insert("", "end", values=list(row))

        total_usd = df_country["Valor USD"].sum()
        self.total_label.configure(
            text=f"{self.current_operation} - {self.current_filename_base} ({self.current_year})   |   Total: US$ {total_usd:,.2f}"
        )

    def _save_table(self, fmt):
        if self.df_country is None:
            messagebox.showwarning("Nada para salvar", "Faca uma pesquisa primeiro.")
            return

        os.makedirs(RESULTS_DIR, exist_ok=True)
        default_name = f"{self.current_filename_base}_{self.current_operation}_{self.current_year}.{fmt}"
        path = filedialog.asksaveasfilename(
            initialdir=RESULTS_DIR,
            initialfile=default_name,
            defaultextension=f".{fmt}",
            filetypes=[(fmt.upper(), f"*.{fmt}")],
        )
        if not path:
            return

        if fmt == "csv":
            self.df_country.to_csv(path, index=False)
        elif fmt == "xlsx":
            self.df_country.to_excel(path, index=False)
        elif fmt == "json":
            self.df_country.to_json(path)

        messagebox.showinfo("Salvo", f"Arquivo salvo em:\n{path}")

    # Chart Tab
    def _build_page_grafico(self, frame):
        ctk.CTkLabel(
            frame, text="Grafico", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(padx=20, pady=(20, 5), anchor="w")

        controls = ctk.CTkFrame(frame, fg_color="transparent")
        controls.pack(padx=20, pady=10, anchor="w")

        ctk.CTkLabel(controls, text="Tipo:").pack(side="left", padx=(0, 10))
        self.chart_type_menu = ctk.CTkOptionMenu(
            controls, values=["Barra horizontal", "Barra vertical", "Pizza"]
        )
        self.chart_type_menu.pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            controls, text="Gerar grafico (Top 10)", command=self._generate_chart
        ).pack(side="left", padx=5)
        ctk.CTkButton(controls, text="Salvar grafico", command=self._save_chart).pack(
            side="left", padx=5
        )

        self.chart_frame = ctk.CTkFrame(frame)
        self.chart_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def _generate_chart(self):
        if self.df_country is None:
            messagebox.showwarning(
                "Sem dados", "Faca uma pesquisa na pagina Pesquisa primeiro."
            )
            return

        top10 = (
            self.df_country.groupby("NCM Description")["Valor USD"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        wrapped_labels = [wrap_label(label, width=22) for label in top10.index]

        chart_type = self.chart_type_menu.get()
        title = f"Top 10 produtos - {self.current_operation} - {self.current_filename_base} ({self.current_year})"

        fig = Figure(figsize=(9, 6), dpi=100)
        ax = fig.add_subplot(111)

        if chart_type == "Barra horizontal":
            ax.barh(wrapped_labels, top10.values, color="#3b8ed0")
            ax.invert_yaxis()  # maior valor no topo
            ax.set_xlabel("Valor USD")
            ax.tick_params(axis="y", labelsize=8)
            fig.subplots_adjust(left=0.38, right=0.95, top=0.88, bottom=0.1)

        elif chart_type == "Barra vertical":
            ax.bar(wrapped_labels, top10.values, color="#3b8ed0")
            ax.set_ylabel("Valor USD")
            ax.tick_params(axis="x", labelsize=7, rotation=30)
            for label in ax.get_xticklabels():
                label.set_ha("right")
            fig.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.32)

        else:  # Gráfico de pizza
            wedges, _, autotexts = ax.pie(
                top10.values,
                labels=None,
                autopct="%1.1f%%",
                textprops={"fontsize": 8},
            )
            ax.legend(
                wedges,
                wrapped_labels,
                loc="center left",
                bbox_to_anchor=(1.0, 0.5),
                fontsize=7,
                frameon=False,
            )
            fig.subplots_adjust(left=0.05, right=0.65, top=0.88, bottom=0.05)

        ax.set_title(title, fontsize=11, wrap=True)

        if self.chart_canvas is not None:
            self.chart_canvas.get_tk_widget().destroy()

        self.current_figure = fig
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _save_chart(self):
        if self.current_figure is None:
            messagebox.showwarning("Nada para salvar", "Gere um grafico primeiro.")
            return

        os.makedirs(RESULTS_DIR, exist_ok=True)
        default_name = f"{self.current_filename_base}_chart_{self.current_operation}_{self.current_year}.png"
        path = filedialog.asksaveasfilename(
            initialdir=RESULTS_DIR,
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if not path:
            return

        self.current_figure.savefig(path, bbox_inches="tight")
        messagebox.showinfo("Salvo", f"Grafico salvo em:\n{path}")

if __name__ == "__main__":
    app = ComexStatApp()
    app.mainloop()
