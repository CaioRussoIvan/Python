from pathlib import Path

from flask import Flask, jsonify, request
from log_service import append_log, read_logs

BASE_DIR = Path(__file__).resolve().parent


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(LOG_FILE=str(BASE_DIR / "app.log"))
    if test_config:
        app.config.update(test_config)

    @app.post("/logs")
    def create_log():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(detail="Entrada JSON inválida."), 422

        level = data.get("level")
        message = data.get("message")

        if not isinstance(level, str) or level not in ("INFO", "WARNING", "ERROR"):
            return jsonify(detail="Nível inválido."), 422

        # Rejeitar quebras de linha antes de remover espaços externos.
        if not isinstance(message, str) or "\n" in message or "\r" in message:
            return jsonify(detail="Mensagem inválida."), 422

        message = message.strip()
        if not 1 <= len(message) <= 200:
            return jsonify(detail="Mensagem inválida."), 422

        entry = f"[{level}] {message}"
        try:
            append_log(entry, app.config["LOG_FILE"])
        except OSError:
            return jsonify(detail="Não foi possível gravar o log."), 500

        return jsonify(status="registrado", entry=entry), 201

    @app.get("/logs")
    def get_logs():
        try:
            logs = read_logs(app.config["LOG_FILE"])
        except OSError:
            return jsonify(detail="Não foi possível ler o log."), 500
        return jsonify(total=len(logs), logs=logs), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


