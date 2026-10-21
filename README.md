# API de Logs com Flask

## Requisitos e versões
- Python 3.10 ou superior
- Flask 3.x
- pytest 8.x
- `unittest` e `tempfile` são módulos da biblioteca padrão.

## Estrutura
```text
log_api/
├── main.py
├── log_service.py
├── requirements.txt
├── README.md
├── resultados_testes.txt
├── app.log                 # criado na primeira gravação; não enviar
└── tests/
    ├── __init__.py
    ├── test_log_service_unittest.py
    └── test_api_pytest.py
```

## Instalação e execução
Na pasta `log_api`, crie e ative um ambiente virtual, se desejar, e execute:

```bash
python -m pip install -r requirements.txt
python main.py
```

A API ficará disponível em `http://127.0.0.1:5000`.

## Uso da API

Registrar um evento:

```bash
curl -i -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level":"INFO","message":"Cadastro concluído."}'
```

Resposta esperada: HTTP 201 e um JSON com `status` e `entry`.

Consultar o histórico:

```bash
curl -i http://127.0.0.1:5000/logs
```

O GET responde HTTP 200 com `total` e `logs`. Se o arquivo ainda não existir ou estiver vazio, retorna `{"total": 0, "logs": []}`. Os níveis aceitos são `INFO`, `WARNING` e `ERROR`. Mensagens precisam conter de 1 a 200 caracteres após a remoção de espaços externos; quebras de linha são rejeitadas.

## Testes

Execute separadamente, a partir da pasta `log_api`:

```bash
python -m unittest discover -s tests -p "test_log_service_unittest.py" -v
python -m pytest tests/test_api_pytest.py -v
```

Os testes usam arquivos temporários próprios e não alteram o `app.log` normal.

## Respostas às perguntas da atividade

**Como uma nova mensagem é acrescentada sem apagar o histórico?**  
A função `append_log` abre o arquivo em modo de acréscimo (`a`), UTF-8, e escreve uma entrada seguida de uma quebra de linha. Esse modo cria o arquivo se necessário e preserva as linhas anteriores.

**Como foi provado que o GET consulta o arquivo, e não uma lista em memória?**  
Os testes verificam o conteúdo persistido no arquivo depois do POST e consultam o endpoint GET. O serviço abre o arquivo novamente a cada leitura, e o teste também confirma que o GET não modifica seus bytes.

**O que cada suíte verifica e como os testes evitam alterar o log normal?**  
`unittest` testa diretamente as funções de escrita e leitura, incluindo persistência, duplicatas, UTF-8 e falhas de I/O. `pytest` usa o cliente de teste do Flask para validar status HTTP, conteúdo, validação, limites e erros. Cada teste usa diretório/arquivo temporário (`TemporaryDirectory` ou `tmp_path`) e injeta o caminho pela configuração `LOG_FILE`.

## Uso de IA
A IA foi utilizada como apoio para estruturar uma implementação inicial, elaborar casos de teste e revisar a documentação. O código e os resultados devem ser conferidos pelo estudante; `resultados_testes.txt` registra as saídas obtidas ao executar as suítes neste ambiente.
