# funções de acesso e manipulação de files
from pathlib import Path
from datetime import datetime
import os, shutil, subprocess, json


# carrega as configurações do user
def _load_conf():
    with open('config/conf.json', 'r', encoding='utf-8') as conf:
        return json.load(conf)


def verify_absolute_dir():
    """
    Verifica/relembra quais são os diretórios raizes disponísveis para atuar.
    """
    config = _load_conf()
    return f"os diretórios base distoníveis para executar tarefas são: {list(config["diretórios"].keys())}"


def list_dir(local: str, dir: str = None) -> list:
    """
    Lista arquivos e pastas dentro de um diretório permitido.
    """

    path = Path(local)

    if dir:
        path = path / dir

    if not path.exists():
        return ["Diretório não encontrado"]

    return [item.name for item in path.iterdir()]


def read_file(local: str, arquivo: str) -> str:
    """
    Lê o conteúdo de um arquivo dentro de um diretório permitido.
    """

    path = Path(local) / arquivo

    if not path.exists():
        return "Arquivo não encontrado"

    return path.read_text(encoding="utf-8")


def write_file(local: str, arquivo: str, conteudo: str) -> str:
    """
    Cria ou substitui o conteúdo de um arquivo dentro de um diretório permitido.
    """

    path = Path(local) / arquivo

    path.write_text(
        conteudo,
        encoding="utf-8"
    )

    return "Arquivo salvo com sucesso"


def create_folder(local: str, nome: str) -> str:
    """
    Cria uma nova pasta dentro de um diretório permitido.
    """

    path = Path(local) / nome

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    return "Pasta criada com sucesso"


def rename_file(local: str, antigo: str, novo: str) -> str:
    """
    Renomeia um arquivo dentro de um diretório permitido.
    """

    origem = Path(local) / antigo
    destino = Path(local) / novo

    origem.rename(destino)

    return "Arquivo renomeado com sucesso"


def move_file(local: str, origem: str, destino: str) -> str:
    """
    Move um arquivo para outro local dentro do diretório permitido.
    """

    origem_path = Path(local) / origem
    destino_path = Path(local) / destino

    shutil.move(
        origem_path,
        destino_path
    )

    return "Arquivo movido com sucesso"


def delete_file(local: str, arquivo: str) -> str:
    """
    Remove um arquivo dentro de um diretório permitido.
    """

    path = Path(local) / arquivo

    if not path.exists():
        return "Arquivo não encontrado"

    path.unlink()

    return "Arquivo removido"


def find_file(local: str, nome: str) -> list:
    """
    Procura arquivos pelo nome dentro de um diretório permitido.
    """

    resultados = []

    base = Path(local)

    for arquivo in base.rglob("*"):
        if nome.lower() in arquivo.name.lower():
            resultados.append(
                str(arquivo.relative_to(base))
            )

    return resultados


def search_files(local: str, termo: str) -> list:
    """
    Procura um texto dentro dos arquivos de um diretório permitido.
    """

    resultados = []

    base = Path(local)

    for arquivo in base.rglob("*"):

        if not arquivo.is_file():
            continue

        try:
            texto = arquivo.read_text(
                encoding="utf-8"
            )

            if termo.lower() in texto.lower():
                resultados.append(
                    str(arquivo.relative_to(base))
                )

        except UnicodeDecodeError:
            continue

    return resultados


def read_multiple_files(local: str, arquivos: list) -> dict:
    """
    Lê vários arquivos de um diretório permitido de uma vez.
    """

    resultado = {}

    for arquivo in arquivos:

        path = Path(local) / arquivo

        if path.exists():
            resultado[arquivo] = path.read_text(
                encoding="utf-8"
            )
        else:
            resultado[arquivo] = "Arquivo não encontrado"

    return resultado


def get_file_metadata(local: str, arquivo: str) -> dict:
    """
    Retorna informações sobre um arquivo.
    """

    path = Path(local) / arquivo

    if not path.exists():
        return {
            "erro": "Arquivo não encontrado"
        }

    info = path.stat()

    return {
        "nome": path.name,
        "tamanho_bytes": info.st_size,
        "modificado": datetime.fromtimestamp(
            info.st_mtime
        ).isoformat()
    }


def get_time() -> str:
    """
    Retorna a data e hora atual do sistema.
    """

    return datetime.now().isoformat()


def get_system_info() -> dict:
    """
    Retorna informações básicas do sistema operacional.
    """

    return {
        "sistema": os.name,
        "usuario": os.getlogin(),
        "diretorio_atual": str(Path.cwd())
    }


def git_status(local: str) -> str:
    """
    Mostra o estado atual de um repositório Git.
    """

    resultado = subprocess.run(
        ["git", "status"],
        cwd=local,
        capture_output=True,
        text=True
    )

    return resultado.stdout


def git_diff(local: str) -> str:
    """
    Mostra as alterações atuais de um repositório Git.
    """

    resultado = subprocess.run(
        ["git", "diff"],
        cwd=local,
        capture_output=True,
        text=True
    )

    return resultado.stdout


def git_log(local: str) -> str:
    """
    Mostra o histórico recente de commits de um repositório Git.
    """

    resultado = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        cwd=local,
        capture_output=True,
        text=True
    )

    return resultado.stdout

