"""Interface gráfica do Conversor HEIC -> PNG/JPG (DUOMO Soluções)."""

import queue
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from abertura import mostrar_abertura
from conversor import EXTENSOES_HEIC, converter, listar_heic

# Paleta da marca DUOMO
FUNDO = "#0B111A"
CARTAO = "#121A26"
CARTAO_CLARO = "#1A2433"
BORDA = "#223047"
AZUL = "#0951B6"
AZUL_HOVER = "#1366D6"
AZUL_CLARO = "#4C8DF0"
TEXTO = "#E8EDF5"
TEXTO_SUAVE = "#8A99B0"
SUCESSO = "#3CC48A"
ERRO = "#F06A6A"


def recurso(nome):
    """Caminho de um arquivo em assets/, também dentro do executável PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "assets" / nome


def resumir(pasta, limite=60):
    """Encurta caminhos longos mantendo o final, que é a parte mais útil."""
    texto = str(pasta)
    return texto if len(texto) <= limite else "…" + texto[-(limite - 1):]


class LinhaArquivo(ctk.CTkFrame):
    """Uma linha da lista: nome, pasta, status e botão de remover."""

    def __init__(self, master, caminho, ao_remover):
        super().__init__(master, fg_color=CARTAO_CLARO, corner_radius=10)
        self.columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="HEIC", width=46, height=26, corner_radius=6,
                     fg_color=AZUL, text_color="white",
                     font=ctk.CTkFont(size=11, weight="bold")
                     ).grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=10)
        ctk.CTkLabel(self, text=caminho.name, anchor="w", text_color=TEXTO,
                     font=ctk.CTkFont(size=13, weight="bold")
                     ).grid(row=0, column=1, sticky="ew", pady=(8, 0))
        ctk.CTkLabel(self, text=resumir(caminho.parent), anchor="w", text_color=TEXTO_SUAVE,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=1, column=1, sticky="ew", pady=(0, 8))
        self.status = ctk.CTkLabel(self, text="", width=90, anchor="e",
                                   font=ctk.CTkFont(size=12))
        self.status.grid(row=0, column=2, rowspan=2, padx=6)
        self.remover = ctk.CTkButton(self, text="✕", width=30, height=30,
                                     fg_color="transparent", hover_color=BORDA,
                                     text_color=TEXTO_SUAVE, command=ao_remover)
        self.remover.grid(row=0, column=3, rowspan=2, padx=(0, 10))

    def definir_status(self, texto, cor):
        self.status.configure(text=texto, text_color=cor)


class ConversorApp(ctk.CTk):
    def __init__(self, abertura=True):
        super().__init__(fg_color=FUNDO)
        self.title("Conversor HEIC · DUOMO Soluções")
        self.geometry("980x660")
        self.minsize(860, 580)
        self._definir_icone()

        self.arquivos = []   # lista de Path, na mesma ordem das linhas
        self.linhas = {}     # Path -> LinhaArquivo
        self.fila = queue.Queue()
        self.convertendo = False

        self.var_formato = ctk.StringVar(value="JPG")
        self.var_qualidade = ctk.IntVar(value=90)
        self.var_metadados = ctk.BooleanVar(value=True)
        self.var_sobrescrever = ctk.BooleanVar(value=False)
        self.var_destino = ctk.StringVar(value="Mesma pasta")
        self.var_pasta_saida = ctk.StringVar()

        self._montar_interface()
        self._atualizar_lista()

        if abertura:
            self.withdraw()
            mostrar_abertura(self, recurso("intro.mp4"), self._exibir)

    def _definir_icone(self):
        try:
            if sys.platform.startswith("win"):
                self.iconbitmap(str(recurso("icon.ico")))
            else:
                self._icone = ImageTk.PhotoImage(Image.open(recurso("logo.png")))
                self.iconphoto(True, self._icone)
        except Exception:  # noqa: BLE001 - ícone é só estético
            pass

    def _exibir(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    # ------------------------------------------------------------ interface
    def _montar_interface(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._montar_cabecalho()

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))
        corpo.columnconfigure(0, weight=1)
        corpo.rowconfigure(0, weight=1)
        self._montar_arquivos(corpo)
        self._montar_opcoes(corpo)
        self._montar_rodape()

    def _montar_cabecalho(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 16))

        logo = ctk.CTkImage(Image.open(recurso("logo.png")), size=(46, 46))
        ctk.CTkLabel(topo, image=logo, text="").pack(side="left")
        textos = ctk.CTkFrame(topo, fg_color="transparent")
        textos.pack(side="left", padx=14)
        ctk.CTkLabel(textos, text="Conversor HEIC", text_color=TEXTO,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(textos, text="DUOMO SOLUÇÕES  ·  HEIC para PNG e JPG",
                     text_color=TEXTO_SUAVE, font=ctk.CTkFont(size=12)).pack(anchor="w")

    def _cartao(self, master, titulo):
        cartao = ctk.CTkFrame(master, fg_color=CARTAO, corner_radius=16,
                              border_width=1, border_color=BORDA)
        ctk.CTkLabel(cartao, text=titulo, text_color=TEXTO,
                     font=ctk.CTkFont(size=15, weight="bold")
                     ).pack(anchor="w", padx=20, pady=(16, 10))
        return cartao

    def _botao(self, master, texto, comando, primario=False, **extra):
        if primario:
            cores = dict(fg_color=AZUL, hover_color=AZUL_HOVER, text_color="white")
        else:
            cores = dict(fg_color=CARTAO_CLARO, hover_color=BORDA, text_color=TEXTO,
                         border_width=1, border_color=BORDA)
        return ctk.CTkButton(master, text=texto, command=comando, corner_radius=10,
                             height=36, **cores, **extra)

    def _montar_arquivos(self, corpo):
        cartao = self._cartao(corpo, "Arquivos")
        cartao.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        barra = ctk.CTkFrame(cartao, fg_color="transparent")
        barra.pack(fill="x", padx=20)
        self._botao(barra, "+  Adicionar arquivos", self.adicionar_arquivos,
                    primario=True).pack(side="left")
        self._botao(barra, "+  Adicionar pasta", self.adicionar_pasta
                    ).pack(side="left", padx=8)
        self._botao(barra, "Limpar", self.limpar_lista, width=80).pack(side="right")

        self.lista = ctk.CTkScrollableFrame(cartao, fg_color="transparent",
                                            scrollbar_button_color=BORDA)
        self.lista.pack(fill="both", expand=True, padx=12, pady=12)
        self.lista.columnconfigure(0, weight=1)

        self.vazio = ctk.CTkFrame(self.lista, fg_color="transparent")
        ctk.CTkLabel(self.vazio, text="⬡", text_color=AZUL_CLARO,
                     font=ctk.CTkFont(size=52)).pack(pady=(50, 4))
        ctk.CTkLabel(self.vazio, text="Nenhuma imagem na lista", text_color=TEXTO,
                     font=ctk.CTkFont(size=15, weight="bold")).pack()
        ctk.CTkLabel(self.vazio, text="Adicione fotos .heic ou uma pasta inteira para começar.",
                     text_color=TEXTO_SUAVE).pack(pady=4)

    def _montar_opcoes(self, corpo):
        cartao = self._cartao(corpo, "Configurações")
        cartao.grid(row=0, column=1, sticky="ns")
        cartao.configure(width=300)

        def rotulo(texto):
            ctk.CTkLabel(cartao, text=texto.upper(), text_color=TEXTO_SUAVE,
                         font=ctk.CTkFont(size=11, weight="bold")
                         ).pack(anchor="w", padx=20, pady=(12, 6))

        def segmentado(variavel, valores, comando=None):
            ctk.CTkSegmentedButton(cartao, values=valores, variable=variavel,
                                   command=comando, height=34, corner_radius=10,
                                   fg_color=CARTAO_CLARO, unselected_color=CARTAO_CLARO,
                                   unselected_hover_color=BORDA, selected_color=AZUL,
                                   selected_hover_color=AZUL_HOVER, text_color=TEXTO
                                   ).pack(fill="x", padx=20)

        rotulo("Formato de saída")
        segmentado(self.var_formato, ["JPG", "PNG", "Ambos"],
                   lambda _v: self._atualizar_qualidade())

        self.quadro_qualidade = ctk.CTkFrame(cartao, fg_color=CARTAO)
        self.quadro_qualidade.pack(fill="x", padx=2)
        cab = ctk.CTkFrame(self.quadro_qualidade, fg_color=CARTAO)
        cab.pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(cab, text="QUALIDADE DO JPG", text_color=TEXTO_SUAVE,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        ctk.CTkLabel(cab, textvariable=self.var_qualidade, text_color=AZUL_CLARO,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")
        self.escala = ctk.CTkSlider(self.quadro_qualidade, from_=10, to=100,
                                    number_of_steps=90, variable=self.var_qualidade,
                                    button_color=AZUL_CLARO, button_hover_color=AZUL_HOVER,
                                    progress_color=AZUL, fg_color=BORDA)
        self.escala.pack(fill="x", padx=18)

        rotulo("Destino")
        segmentado(self.var_destino, ["Mesma pasta", "Outra pasta"],
                   lambda _v: self._atualizar_destino())
        self.botao_saida = self._botao(cartao, "Escolher pasta...", self.escolher_saida)
        self.botao_saida.pack(fill="x", padx=20, pady=(8, 0))
        self.rotulo_saida = ctk.CTkLabel(cartao, text="", text_color=TEXTO_SUAVE,
                                         font=ctk.CTkFont(size=11), wraplength=250,
                                         justify="left", anchor="w")
        self.rotulo_saida.pack(fill="x", padx=20, pady=(4, 0))

        rotulo("Opções")
        for texto, var in (("Manter metadados (EXIF)", self.var_metadados),
                           ("Sobrescrever existentes", self.var_sobrescrever)):
            ctk.CTkSwitch(cartao, text=texto, variable=var, text_color=TEXTO,
                          progress_color=AZUL, button_color=TEXTO,
                          button_hover_color="white", fg_color=BORDA
                          ).pack(anchor="w", padx=20, pady=5)
        ctk.CTkFrame(cartao, fg_color="transparent", height=10).pack()

        self._atualizar_destino()

    def _montar_rodape(self):
        rodape = ctk.CTkFrame(self, fg_color=CARTAO, corner_radius=16,
                              border_width=1, border_color=BORDA)
        rodape.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 20))
        rodape.columnconfigure(0, weight=1)

        self.rotulo_status = ctk.CTkLabel(rodape, text="", anchor="w", text_color=TEXTO,
                                          font=ctk.CTkFont(size=13))
        self.rotulo_status.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 4))
        self.progresso = ctk.CTkProgressBar(rodape, height=8, corner_radius=4,
                                            fg_color=BORDA, progress_color=AZUL_CLARO)
        self.progresso.set(0)
        self.progresso.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))
        self.botao_converter = ctk.CTkButton(
            rodape, text="Converter", command=self.iniciar_conversao, width=180,
            height=46, corner_radius=12, fg_color=AZUL, hover_color=AZUL_HOVER,
            font=ctk.CTkFont(size=15, weight="bold"))
        self.botao_converter.grid(row=0, column=1, rowspan=2, padx=(0, 16), pady=14)

    def _atualizar_qualidade(self):
        estado = "disabled" if self.var_formato.get() == "PNG" else "normal"
        self.escala.configure(state=estado)

    def _atualizar_destino(self):
        outra = self.var_destino.get() == "Outra pasta"
        self.botao_saida.configure(state="normal" if outra else "disabled")
        pasta = self.var_pasta_saida.get()
        if not outra:
            texto = "As imagens são salvas ao lado do arquivo original."
        else:
            texto = pasta or "Nenhuma pasta escolhida."
        self.rotulo_saida.configure(text=texto)

    def _status(self, texto):
        self.rotulo_status.configure(text=texto)

    # ------------------------------------------------------------- arquivos
    def _atualizar_lista(self):
        if self.arquivos:
            self.vazio.grid_forget()
            self._status(f"{len(self.arquivos)} arquivo(s) prontos para converter.")
        else:
            self.vazio.grid(row=0, column=0, sticky="nsew")
            self._status("Adicione arquivos .heic para começar.")
        self.progresso.set(0)

    def _adicionar(self, caminhos):
        for caminho in map(Path, caminhos):
            if caminho.suffix.lower() not in EXTENSOES_HEIC or caminho in self.linhas:
                continue
            linha = LinhaArquivo(self.lista, caminho,
                                 lambda c=caminho: self.remover(c))
            linha.grid(row=len(self.arquivos) + 1, column=0, sticky="ew", pady=4)
            self.arquivos.append(caminho)
            self.linhas[caminho] = linha
        self._atualizar_lista()

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

    def remover(self, caminho):
        if self.convertendo:
            return
        self.linhas.pop(caminho).destroy()
        self.arquivos.remove(caminho)
        self._atualizar_lista()

    def limpar_lista(self):
        if self.convertendo:
            return
        for linha in self.linhas.values():
            linha.destroy()
        self.linhas.clear()
        self.arquivos.clear()
        self._atualizar_lista()

    def escolher_saida(self):
        pasta = filedialog.askdirectory(title="Pasta de destino")
        if pasta:
            self.var_pasta_saida.set(pasta)
            self._atualizar_destino()

    # ------------------------------------------------------------ conversão
    def iniciar_conversao(self):
        if self.convertendo:
            return
        if not self.arquivos:
            messagebox.showwarning("Aviso", "Adicione ao menos um arquivo .heic.")
            return
        escolha = self.var_formato.get()
        formatos = ["PNG", "JPG"] if escolha == "Ambos" else [escolha]
        pasta_saida = None
        if self.var_destino.get() == "Outra pasta":
            pasta_saida = self.var_pasta_saida.get().strip()
            if not pasta_saida:
                messagebox.showwarning("Aviso", "Escolha a pasta de destino.")
                return

        opcoes = dict(formatos=formatos, pasta_saida=pasta_saida,
                      qualidade=self.var_qualidade.get(),
                      manter_metadados=self.var_metadados.get(),
                      sobrescrever=self.var_sobrescrever.get())

        self.convertendo = True
        self.botao_converter.configure(state="disabled", text="Convertendo...")
        for linha in self.linhas.values():
            linha.definir_status("aguardando", TEXTO_SUAVE)
        self.progresso.set(0)
        threading.Thread(target=self._trabalhador,
                         args=(list(self.arquivos), opcoes), daemon=True).start()
        self.after(100, self._verificar_fila)

    def _trabalhador(self, arquivos, opcoes):
        """Roda em outra thread para a janela não travar durante a conversão."""
        erros = []
        for i, arquivo in enumerate(arquivos, start=1):
            try:
                converter(arquivo, **opcoes)
                self.fila.put(("arquivo", arquivo, None))
            except Exception as exc:  # noqa: BLE001 - reporta qualquer falha ao usuário
                erros.append(f"{arquivo.name}: {exc}")
                self.fila.put(("arquivo", arquivo, str(exc)))
            self.fila.put(("progresso", i, len(arquivos), arquivo.name))
        self.fila.put(("fim", len(arquivos), erros))

    def _verificar_fila(self):
        try:
            while True:
                msg = self.fila.get_nowait()
                if msg[0] == "arquivo":
                    _, arquivo, erro = msg
                    linha = self.linhas.get(arquivo)
                    if linha:
                        linha.definir_status("✕ erro" if erro else "✓ pronto",
                                             ERRO if erro else SUCESSO)
                elif msg[0] == "progresso":
                    _, i, total, nome = msg
                    self.progresso.set(i / total)
                    self._status(f"Convertendo {i} de {total}  ·  {nome}")
                else:
                    self._finalizar(*msg[1:])
                    return
        except queue.Empty:
            pass
        self.after(100, self._verificar_fila)

    def _finalizar(self, total, erros):
        self.convertendo = False
        self.botao_converter.configure(state="normal", text="Converter")
        ok = total - len(erros)
        self._status(f"Concluído: {ok} de {total} arquivo(s) convertido(s).")
        if erros:
            detalhes = "\n".join(erros[:15])
            if len(erros) > 15:
                detalhes += f"\n... e mais {len(erros) - 15} erro(s)."
            messagebox.showerror("Conversão com erros", detalhes)
        else:
            messagebox.showinfo("Pronto", f"{ok} arquivo(s) convertido(s) com sucesso!")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ConversorApp(abertura="--sem-abertura" not in sys.argv).mainloop()
