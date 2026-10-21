import pytest

from main import create_app


@pytest.fixture
def setup_api(tmp_path):
    log_file = tmp_path / "test-app.log"
    app = create_app({"TESTING": True, "LOG_FILE": str(log_file)})
    return app.test_client(), log_file


def read_file(path):
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def test_p1_initial_get_is_empty(setup_api):
    client, _ = setup_api
    response = client.get("/logs")
    assert response.status_code == 200
    assert response.get_json() == {"total": 0, "logs": []}


@pytest.mark.parametrize("level", ["INFO", "WARNING", "ERROR"])
def test_p2_valid_post_writes_line_for_each_level(setup_api, level):
    client, path = setup_api
    response = client.post("/logs", json={"level": level, "message": "  Cadastro concluído.  "})
    expected = f"[{level}] Cadastro concluído."
    assert response.status_code == 201
    assert response.get_json() == {"status": "registrado", "entry": expected}
    assert read_file(path) == [expected]


def test_p3_two_posts_get_order_and_get_does_not_modify_file(setup_api):
    client, path = setup_api
    client.post("/logs", json={"level": "INFO", "message": "Um."})
    client.post("/logs", json={"level": "ERROR", "message": "Dois."})
    before = path.read_bytes()
    response = client.get("/logs")
    assert response.status_code == 200
    assert response.get_json() == {
        "total": 2,
        "logs": ["[INFO] Um.", "[ERROR] Dois."]
    }
    assert path.read_bytes() == before


def test_p4_repeated_posts_create_two_entries(setup_api):
    client, path = setup_api
    payload = {"level": "INFO", "message": "Evento repetido."}
    assert client.post("/logs", json=payload).status_code == 201
    assert client.post("/logs", json=payload).status_code == 201
    assert read_file(path) == ["[INFO] Evento repetido.", "[INFO] Evento repetido."]


@pytest.mark.parametrize("message", ["", "   ", 123, None, "linha1\nlinha2", "linha1\rlinha2", "x" * 201])
def test_p5_invalid_messages_do_not_change_existing_history(setup_api, message):
    client, path = setup_api
    client.post("/logs", json={"level": "INFO", "message": "Registro válido."})
    before = path.read_bytes()
    response = client.post("/logs", json={"level": "INFO", "message": message})
    assert response.status_code == 422
    assert path.read_bytes() == before


@pytest.mark.parametrize("message", ["x", "x" * 200])
def test_p5_accepts_boundary_lengths_and_trims_outer_spaces(setup_api, message):
    client, path = setup_api
    response = client.post("/logs", json={"level": "INFO", "message": f"  {message}  "})
    assert response.status_code == 201
    assert read_file(path) == [f"[INFO] {message}"]


@pytest.mark.parametrize("level", ["DEBUG", "info", "", None, 3])
def test_p6_invalid_levels_do_not_change_file(setup_api, level):
    client, path = setup_api
    client.post("/logs", json={"level": "INFO", "message": "Registro válido."})
    before = path.read_bytes()
    response = client.post("/logs", json={"level": level, "message": "Inválido."})
    assert response.status_code == 422
    assert path.read_bytes() == before


@pytest.mark.parametrize("payload", [{"message": "Sem nível."}, {"level": "INFO"}, {}])
def test_p7_missing_required_fields(setup_api, payload):
    client, path = setup_api
    response = client.post("/logs", json=payload)
    assert response.status_code == 422
    assert not path.exists()


def test_p7_null_and_non_object_json_are_rejected(setup_api):
    client, path = setup_api
    assert client.post("/logs", json=None).status_code == 422
    assert client.post("/logs", data='"texto"', content_type="application/json").status_code == 422
    assert not path.exists()


def test_p8_write_failure_returns_safe_500(setup_api):
    client, path = setup_api
    path.mkdir()
    response = client.post("/logs", json={"level": "INFO", "message": "Teste."})
    assert response.status_code == 500
    assert response.get_json() == {"detail": "Não foi possível gravar o log."}
    assert "Traceback" not in response.get_data(as_text=True)


def test_p8_read_failure_returns_safe_500(setup_api):
    client, path = setup_api
    path.mkdir()
    response = client.get("/logs")
    assert response.status_code == 500
    assert response.get_json() == {"detail": "Não foi possível ler o log."}
    assert "Traceback" not in response.get_data(as_text=True)
