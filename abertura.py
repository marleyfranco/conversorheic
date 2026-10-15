"""Tela de abertura que reproduz o vídeo da marca antes da janela principal.

O vídeo é decodificado com PyAV e desenhado quadro a quadro numa janela sem
bordas. O áudio é tocado com `sounddevice` quando disponível; se não estiver,
a abertura roda sem som. Clique no vídeo ou pressione Esc para pular.
"""

import time
import tkinter as tk

from PIL import Image, ImageTk

try:
    import av
except ImportError:  # sem PyAV não há abertura, o app abre direto
    av = None

try:
    import sounddevice as sd
except (ImportError, OSError):  # OSError: PortAudio ausente no sistema
    sd = None


class Abertura(tk.Toplevel):
    def __init__(self, master, video, ao_terminar, com_som=True):
        # Abre o vídeo antes de criar a janela: se falhar, nada fica na tela.
        self.container = av.open(str(video))
        stream = self.container.streams.video[0]
        self.fps = float(stream.average_rate or 24)
        self.quadros = self.container.decode(stream)

        super().__init__(master)
        self.ao_terminar = ao_terminar
        self.encerrada = False
        self.som = False

        # Mantém a proporção do vídeo ocupando no máximo 80% da altura da tela.
        largura, altura = stream.codec_context.width, stream.codec_context.height
        escala = min(1.0, self.winfo_screenheight() * 0.8 / altura,
                     self.winfo_screenwidth() * 0.8 / largura)
        self.tamanho = (int(largura * escala), int(altura * escala))
        x = (self.winfo_screenwidth() - self.tamanho[0]) // 2
        y = (self.winfo_screenheight() - self.tamanho[1]) // 2

        self.overrideredirect(True)
        self.configure(bg="black")
        self.geometry(f"{self.tamanho[0]}x{self.tamanho[1]}+{x}+{y}")
        self.attributes("-topmost", True)

        self.tela = tk.Label(self, bg="black", bd=0, cursor="hand2")
        self.tela.pack(fill="both", expand=True)
        pular = tk.Label(self, text="Pular  ›", fg="#C9D6EA", bg="#0B111A",
                         font=("Segoe UI", 10), padx=10, pady=4, cursor="hand2")
        pular.place(relx=1.0, x=-12, y=12, anchor="ne")

        for widget in (self, self.tela, pular):
            widget.bind("<Button-1>", lambda _e: self.encerrar())
        self.bind("<Escape>", lambda _e: self.encerrar())
        self.focus_force()

        if com_som:
            self._tocar_audio(video)
        self.inicio = time.perf_counter()
        self.indice = -1
        self._proximo_quadro()

    def _tocar_audio(self, video):
        if sd is None:
            return
        try:
            with av.open(str(video)) as arquivo:
                if not arquivo.streams.audio:
                    return
                taxa = arquivo.streams.audio[0].rate
                reamostrador = av.AudioResampler(format="flt", layout="stereo", rate=taxa)
                blocos = []
                for frame in arquivo.decode(audio=0):
                    for convertido in reamostrador.resample(frame):
                        blocos.append(convertido.to_ndarray().reshape(-1, 2))
            import numpy as np
            sd.play(np.concatenate(blocos), taxa)
            self.som = True
        except Exception:  # noqa: BLE001 - som é opcional, nunca impede a abertura
            self.som = False

    def _proximo_quadro(self):
        if self.encerrada:
            return
        # Sincroniza pelo relógio: se o computador atrasar, descarta quadros.
        alvo = int((time.perf_counter() - self.inicio) * self.fps)
        quadro = None
        try:
            while self.indice < alvo:
                quadro = next(self.quadros)
                self.indice += 1
        except StopIteration:
            self.encerrar()
            return
        if quadro is not None:
            imagem = quadro.to_image().resize(self.tamanho, Image.BILINEAR)
            self.foto = ImageTk.PhotoImage(imagem)  # referência evita coleta de lixo
            self.tela.configure(image=self.foto)
        espera = (self.indice + 1) / self.fps - (time.perf_counter() - self.inicio)
        self.after(max(1, int(espera * 1000)), self._proximo_quadro)

    def encerrar(self):
        if self.encerrada:
            return
        self.encerrada = True
        if self.som:
            sd.stop()
        self.container.close()
        self.destroy()
        self.ao_terminar()


def mostrar_abertura(master, video, ao_terminar, com_som=True):
    """Exibe a abertura; se não for possível, chama `ao_terminar` direto."""
    if av is None or not video.exists():
        ao_terminar()
        return None
    try:
        return Abertura(master, video, ao_terminar, com_som)
    except Exception:  # noqa: BLE001 - vídeo inválido não deve impedir o app
        ao_terminar()
        return None
