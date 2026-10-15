# Conversor HEIC → PNG / JPG · DUOMO Soluções

Ferramenta com interface gráfica moderna (CustomTkinter, tema escuro com as
cores da DUOMO Soluções) para converter fotos `.heic` / `.heif` (padrão do
iPhone) em `.png` e/ou `.jpg`. Ao abrir, exibe o vídeo de abertura da marca.

## Recursos

- Vídeo de abertura da marca (clique ou `Esc` para pular)
- Seleção de vários arquivos ou de uma pasta inteira (com opção de incluir subpastas)
- Conversão para PNG, JPG ou ambos de uma vez
- Ajuste de qualidade do JPG (10–100)
- Corrige a rotação da foto usando o EXIF e (opcionalmente) mantém os metadados
- Imagens com transparência recebem fundo branco ao virar JPG
- Salva na mesma pasta do original ou em outra pasta escolhida
- Não sobrescreve arquivos existentes (cria `foto_1.jpg`), a menos que você marque a opção
- Status por arquivo (pronto / erro) e barra de progresso; a conversão roda em
  segundo plano, sem travar a janela

## Instalação

Requer Python 3.9+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

> No Linux, o Tkinter pode precisar ser instalado à parte:
> `sudo apt install python3-tk`

## Uso

```bash
python app.py                 # com vídeo de abertura
python app.py --sem-abertura  # abre direto na janela principal
```

O som da abertura usa `sounddevice`. No Linux ele precisa da PortAudio
(`sudo apt install libportaudio2`); sem ela a abertura roda sem som.

1. Clique em **Adicionar arquivos...** ou **Adicionar pasta...**
2. Marque **PNG** e/ou **JPG** e ajuste as opções
3. Clique em **Converter**

A lógica de conversão fica em `conversor.py` e pode ser usada sem a interface:

```python
from conversor import converter
converter("IMG_0001.HEIC", ["PNG", "JPG"], pasta_saida="convertidas", qualidade=85)
```

## Gerar um executável (opcional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ConversorHEIC --icon assets/icon.ico ^
  --add-data "assets;assets" --collect-all pillow_heif --collect-all customtkinter --collect-all av app.py
```

No Linux/macOS troque `^` por `\` e `assets;assets` por `assets:assets`.
O executável ficará em `dist/`.

## Estrutura

| Arquivo | Função |
| --- | --- |
| `app.py` | Janela principal |
| `abertura.py` | Tela de abertura com o vídeo da marca |
| `conversor.py` | Conversão HEIC → PNG/JPG (pode ser usada sem interface) |
| `assets/` | Vídeo de abertura, logo e ícone |
