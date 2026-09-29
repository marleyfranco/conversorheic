"""Interface gráfica (Tkinter) do Conversor HEIC -> PNG/JPG."""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from conversor import EXTENSOES_HEIC, converter, listar_heic


class ConversorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor HEIC → PNG / JPG")
        self.geometry("720x540")
        self.minsize(600, 460)

        self.arquivos = []
        self.fila = queue.Queue()
        self.convertendo = False

        self.var_png = tk.BooleanVar(value=False)
        self.var_jpg = tk.BooleanVar(value=True)
        self.var_qualidade = tk.IntVar(value=90)
        self.var_metadados = tk.BooleanVar(value=True)
        self.var_sobrescrever = tk.BooleanVar(value=False)
        self.var_mesma_pasta = tk.BooleanVar(value=True)
        self.var_pasta_saida = tk.StringVar()
        self.var_status = tk.StringVar(value="Adicione arquivos .heic para começar.")

        self._montar_interface()
        self._atualizar_estado_saida()

    # ------------------------------------------------------------ interface
    def _montar_interface(self):
        pad = {"padx": 10, "pady": 5}

        # Lista de arquivos
        quadro_arq = ttk.LabelFrame(self, text="Arquivos HEIC")
        quadro_arq.pack(fill="both", expand=True, **pad)

        botoes = ttk.Frame(quadro_arq)
        botoes.pack(fill="x", padx=5, pady=5)
        ttk.Button(botoes, text="Adicionar arquivos...",
                   command=self.adicionar_arquivos).pack(side="left")
        ttk.Button(botoes, text="Adicionar pasta...",
                   command=self.adicionar_pasta).pack(side="left", padx=5)
        ttk.Button(botoes, text="Remover selecionados",
                   command=self.remover_selecionados).pack(side="left")
        ttk.Button(botoes, text="Limpar lista",
                   command=self.limpar_lista).pack(side="left", padx=5)

        lista_frame = ttk.Frame(quadro_arq)
        lista_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.lista = tk.Listbox(lista_frame, selectmode="extended")
        barra = ttk.Scrollbar(lista_frame, orient="vertical",
                              command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra.set)
        self.lista.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        # Opções
        quadro_opc = ttk.LabelFrame(self, text="Opções")
        quadro_opc.pack(fill="x", **pad)

        linha1 = ttk.Frame(quadro_opc)
        linha1.pack(fill="x", padx=5, pady=3)
        ttk.Label(linha1, text="Converter para:").pack(side="left")
        ttk.Checkbutton(linha1, text="PNG", variable=self.var_png).pack(side="left", padx=5)
        ttk.Checkbutton(linha1, text="JPG", variable=self.var_jpg,
                        command=self._atualizar_estado_qualidade).pack(side="left")
        ttk.Label(linha1, text="   Qualidade JPG:").pack(side="left")
        self.escala = ttk.Scale(linha1, from_=10, to=100, variable=self.var_qualidade,
                                command=lambda v: self.var_qualidade.set(int(float(v))))
        self.escala.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(linha1, textvariable=self.var_qualidade, width=4).pack(side="left")

        linha2 = ttk.Frame(quadro_opc)
        linha2.pack(fill="x", padx=5, pady=3)
        ttk.Checkbutton(linha2, text="Manter metadados (EXIF)",
                        variable=self.var_metadados).pack(side="left")
        ttk.Checkbutton(linha2, text="Sobrescrever arquivos existentes",
                        variable=self.var_sobrescrever).pack(side="left", padx=10)

        linha3 = ttk.Frame(quadro_opc)
        linha3.pack(fill="x", padx=5, pady=3)
        ttk.Checkbutton(linha3, text="Salvar na mesma pasta do original",
                        variable=self.var_mesma_pasta,
                        command=self._atualizar_estado_saida).pack(side="left")
        self.entrada_saida = ttk.Entry(linha3, textvariable=self.var_pasta_saida)
        self.entrada_saida.pack(side="left", fill="x", expand=True, padx=5)
        self.botao_saida = ttk.Button(linha3, text="Escolher...",
                                      command=self.escolher_saida)
        self.botao_saida.pack(side="left")

        # Progresso e ação
        quadro_prog = ttk.Frame(self)
        quadro_prog.pack(fill="x", **pad)
        self.progresso = ttk.Progressbar(quadro_prog, mode="determinate")
        self.progresso.pack(fill="x")
        ttk.Label(quadro_prog, textvariable=self.var_status).pack(anchor="w", pady=3)

        self.botao_converter = ttk.Button(self, text="Converter",
                                          command=self.iniciar_conversao)
        self.botao_converter.pack(pady=(0, 10))

    def _atualizar_estado_saida(self):
        estado = "disabled" if self.var_mesma_pasta.get() else "normal"
        self.entrada_saida.configure(state=estado)
        self.botao_saida.configure(state=estado)

    def _atualizar_estado_qualidade(self):
        self.escala.configure(state="normal" if self.var_jpg.get() else "disabled")

    # ------------------------------------------------------------- arquivos
    def _adicionar(self, caminhos):
        existentes = set(self.arquivos)
        novos = [Path(c) for c in caminhos
                 if Path(c).suffix.lower() in EXTENSOES_HEIC and Path(c) not in existentes]
        for caminho in novos:
            self.arquivos.append(caminho)
            self.lista.insert("end", str(caminho))
        self.var_status.set(f"{len(self.arquivos)} arquivo(s) na lista.")

    def adicionar_arquivos(self):
        caminhos = filedialog.askopenfilenames(
            title="Selecione imagens HEIC",
            filetypes=[("Imagens HEIC", "*.heic *.HEIC *.heif *.HEIF"),
                       ("Todos os arquivos", "*.*")])
        self._adicionar(caminhos)

    def adicionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione uma pasta com imagens HEIC")
        if not pasta:
            return
        recursivo = messagebox.askyesno("Subpastas", "Incluir também as subpastas?")
        encontrados = listar_heic(pasta, recursivo)
        if not encontrados:
            messagebox.showinfo("Nada encontrado", "Nenhum arquivo .heic nesta pasta.")
        self._adicionar(encontrados)

    def remover_selecionados(self):
        for indice in reversed(self.lista.curselection()):
            self.lista.delete(indice)
            del self.arquivos[indice]
        self.var_status.set(f"{len(self.arquivos)} arquivo(s) na lista.")

    def limpar_lista(self):
        self.lista.delete(0, "end")
        self.arquivos.clear()
        self.var_status.set("Lista vazia.")

    def escolher_saida(self):
        pasta = filedialog.askdirectory(title="Pasta de destino")
        if pasta:
            self.var_pasta_saida.set(pasta)

    # ------------------------------------------------------------ conversão
    def iniciar_conversao(self):
        if self.convertendo:
            return
        formatos = [f for f, v in (("PNG", self.var_png), ("JPG", self.var_jpg)) if v.get()]
        if not self.arquivos:
            messagebox.showwarning("Aviso", "Adicione ao menos um arquivo .heic.")
            return
        if not formatos:
            messagebox.showwarning("Aviso", "Escolha ao menos um formato (PNG ou JPG).")
            return
        pasta_saida = None
        if not self.var_mesma_pasta.get():
            pasta_saida = self.var_pasta_saida.get().strip()
            if not pasta_saida:
                messagebox.showwarning("Aviso", "Escolha a pasta de destino.")
                return

        opcoes = dict(formatos=formatos, pasta_saida=pasta_saida,
                      qualidade=self.var_qualidade.get(),
                      manter_metadados=self.var_metadados.get(),
                      sobrescrever=self.var_sobrescrever.get())

        self.convertendo = True
        self.botao_converter.configure(state="disabled")
        self.progresso.configure(maximum=len(self.arquivos), value=0)
        threading.Thread(target=self._trabalhador,
                         args=(list(self.arquivos), opcoes), daemon=True).start()
        self.after(100, self._verificar_fila)

    def _trabalhador(self, arquivos, opcoes):
        """Roda em outra thread para a janela não travar durante a conversão."""
        erros = []
        for i, arquivo in enumerate(arquivos, start=1):
            try:
                converter(arquivo, **opcoes)
            except Exception as exc:  # noqa: BLE001 - reporta qualquer falha ao usuário
                erros.append(f"{arquivo.name}: {exc}")
            self.fila.put(("progresso", i, len(arquivos), arquivo.name))
        self.fila.put(("fim", len(arquivos), erros))

    def _verificar_fila(self):
        try:
            while True:
                msg = self.fila.get_nowait()
                if msg[0] == "progresso":
                    _, i, total, nome = msg
                    self.progresso.configure(value=i)
                    self.var_status.set(f"Convertendo {i}/{total}: {nome}")
                else:
                    self._finalizar(*msg[1:])
                    return
        except queue.Empty:
            pass
        self.after(100, self._verificar_fila)

    def _finalizar(self, total, erros):
        self.convertendo = False
        self.botao_converter.configure(state="normal")
        ok = total - len(erros)
        self.var_status.set(f"Concluído: {ok} de {total} arquivo(s) convertido(s).")
        if erros:
            detalhes = "\n".join(erros[:15])
            if len(erros) > 15:
                detalhes += f"\n... e mais {len(erros) - 15} erro(s)."
            messagebox.showerror("Conversão com erros", detalhes)
        else:
            messagebox.showinfo("Pronto", f"{ok} arquivo(s) convertido(s) com sucesso!")


if __name__ == "__main__":
    ConversorApp().mainloop()
