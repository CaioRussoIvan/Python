from pathlib import Path


DEFAULT_LOG_FILE = Path(__file__).resolve().parent / "app.log"


def append_log(entry, path=DEFAULT_LOG_FILE):
    """Acrescenta uma entrada como uma única linha UTF-8, sem apagar o histórico."""
    log_path = Path(path)
    with log_path.open("a", encoding="utf-8", newline="") as file:
        file.write(entry + "\n")


def read_logs(path=DEFAULT_LOG_FILE):
    """Lê as entradas em ordem; arquivo inexistente equivale a histórico vazio."""
    log_path = Path(path)
    try:
        with log_path.open("r", encoding="utf-8") as file:
            return [line.rstrip("\r\n") for line in file]
    except FileNotFoundError:
        return []
