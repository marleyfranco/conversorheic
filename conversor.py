"""Lógica de conversão de imagens HEIC/HEIF para PNG e JPG."""

from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

EXTENSOES_HEIC = {".heic", ".heif"}
FORMATOS = {"PNG": ".png", "JPG": ".jpg"}


def listar_heic(pasta, recursivo=False):
    """Retorna os arquivos .heic/.heif de uma pasta, em ordem alfabética."""
    padrao = "**/*" if recursivo else "*"
    return sorted(
        p for p in Path(pasta).glob(padrao)
        if p.is_file() and p.suffix.lower() in EXTENSOES_HEIC
    )


def caminho_destino(origem, formato, pasta_saida=None, sobrescrever=False):
    """Monta o caminho de saída, evitando sobrescrever arquivos existentes."""
    origem = Path(origem)
    pasta = Path(pasta_saida) if pasta_saida else origem.parent
    destino = pasta / (origem.stem + FORMATOS[formato])
    contador = 1
    while destino.exists() and not sobrescrever:
        destino = pasta / f"{origem.stem}_{contador}{FORMATOS[formato]}"
        contador += 1
    return destino


def converter(origem, formatos, pasta_saida=None, qualidade=90,
              manter_metadados=True, sobrescrever=False):
    """Converte um arquivo HEIC para os formatos pedidos ("PNG" e/ou "JPG").

    Retorna a lista de caminhos gerados.
    """
    if pasta_saida:
        Path(pasta_saida).mkdir(parents=True, exist_ok=True)

    gerados = []
    with Image.open(origem) as img:
        # Aplica a rotação indicada no EXIF para a foto não sair "deitada".
        img = ImageOps.exif_transpose(img)
        exif = img.info.get("exif") if manter_metadados else None
        icc = img.info.get("icc_profile")

        for formato in formatos:
            destino = caminho_destino(origem, formato, pasta_saida, sobrescrever)
            opcoes = {}
            if icc:
                opcoes["icc_profile"] = icc
            if exif:
                opcoes["exif"] = exif

            if formato == "JPG":
                imagem = img
                if img.mode not in ("RGB", "L"):
                    # JPG não suporta transparência: aplica fundo branco.
                    rgba = img.convert("RGBA")
                    imagem = Image.new("RGB", rgba.size, (255, 255, 255))
                    imagem.paste(rgba, mask=rgba.getchannel("A"))
                imagem.save(destino, "JPEG", quality=qualidade,
                            optimize=True, **opcoes)
            else:
                img.save(destino, "PNG", optimize=True, **opcoes)
            gerados.append(destino)
    return gerados
