# funções de acesso e manipulação de files
from pathlib import Path


def read_file(local, arquivo):
    """
    Lê o conteúdo de um arquivo.

    Args:
        local: caminho absoluto do diretório permitido.
        arquivo: caminho relativo do arquivo dentro desse diretório.
    """
    full = Path(base_dir) / arquivo
    return full.read_text(encoding="utf-8")


def list_dir(local, dir=None):
    """
    Lista os arquivos e pastas de um diretório permitido.

    Args:
        local: caminho absoluto do diretório permitido.
        dir: caminho relativo da pasta que será listada. Se omitido, lista a raiz.
    """
    path = Path(local)

    if dir:
        path = path / dir

    return [p.name for p in path.iterdir()]


def write_file(local, arquivo, conteudo):
    """
    Escreve ou substitui o conteúdo de um arquivo.

    Args:
        local: caminho absoluto do diretório permitido.
        arquivo: caminho relativo do arquivo.
        conteudo: texto que será escrito.
    """
    full = Path(local) / arquivo
    full.write_text(conteudo, encoding="utf-8")
    return "ok"

