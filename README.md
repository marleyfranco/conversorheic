# Conversor HEIC → PNG / JPG

Ferramenta com interface gráfica (Tkinter) para converter fotos `.heic` / `.heif`
(padrão do iPhone) em `.png` e/ou `.jpg`.

## Recursos

- Seleção de vários arquivos ou de uma pasta inteira (com opção de incluir subpastas)
- Conversão para PNG, JPG ou ambos de uma vez
- Ajuste de qualidade do JPG (10–100)
- Corrige a rotação da foto usando o EXIF e (opcionalmente) mantém os metadados
- Imagens com transparência recebem fundo branco ao virar JPG
- Salva na mesma pasta do original ou em outra pasta escolhida
- Não sobrescreve arquivos existentes (cria `foto_1.jpg`), a menos que você marque a opção
- Barra de progresso; a conversão roda em segundo plano, sem travar a janela

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
python app.py
```

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
pyinstaller --onefile --windowed --name ConversorHEIC --collect-all pillow_heif app.py
```

O executável ficará em `dist/`.
