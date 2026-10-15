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

## Instalar no Windows (sem Python)

Baixe o instalador na página **Releases** do repositório (ou em **Actions** →
último build → *Artifacts*) e execute `ConversorHEIC-Setup-<versão>.exe`.
Ele não pede permissão de administrador, cria atalho no Menu Iniciar (e, se
quiser, na Área de Trabalho) e aparece em "Adicionar ou remover programas".

Também é gerada uma versão portátil (`ConversorHEIC-Portatil-<versão>.zip`):
basta descompactar e abrir `ConversorHEIC.exe`.

> Como o executável não é assinado digitalmente, o Windows SmartScreen pode
> avisar "O Windows protegeu o computador". Clique em **Mais informações** →
> **Executar assim mesmo**.

### Como os instaladores são gerados

O GitHub Actions (`.github/workflows/build-windows.yml`) monta o programa numa
máquina Windows a cada push, testa o executável (`--autoteste`) e guarda os
arquivos em *Artifacts*. Para publicar uma versão oficial em **Releases**,
crie uma tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

### Gerar no seu próprio Windows

Com Python 3.10+ instalado (e, para o instalador, o
[Inno Setup 6](https://jrsoftware.org/isdl.php)):

```bat
build_windows.bat 1.0.0
```

Resultado: `dist\ConversorHEIC\ConversorHEIC.exe` e
`dist\ConversorHEIC-Setup-1.0.0.exe`.

## Estrutura

| Arquivo | Função |
| --- | --- |
| `app.py` | Janela principal |
| `abertura.py` | Tela de abertura com o vídeo da marca |
| `conversor.py` | Conversão HEIC → PNG/JPG (pode ser usada sem interface) |
| `assets/` | Vídeo de abertura, logo e ícone |
| `build_windows.bat` | Gera o executável e o instalador no Windows |
| `installer/ConversorHEIC.iss` | Script do instalador (Inno Setup) |
