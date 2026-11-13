# Plataforma de Rastreio de Ativos IoT

Base inicial em FastAPI para rastreio por IMEI, MAC Address e Cell ID, seguindo o fluxo:

`Torre celular/dispositivo IoT -> MQTT/HTTPS -> Gateway API -> processador de stream -> PostgreSQL/TimescaleDB + Redis -> aplicação cliente`

## Executar

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
# alternativa equivalente
python app.py
```

Documentação interativa: <http://127.0.0.1:8000/docs>

## Stack completa com Docker

Copie `.env.example` para `.env` e execute:

```powershell
docker compose up --build
```

Esse perfil inicia a API, PostgreSQL com PostGIS/TimescaleDB, Redis e Kafka em modo KRaft. O tópico `iot.location-events` é o contrato recomendado para o processador de stream; a API atual mantém a persistência síncrona como fallback enquanto o consumidor Kafka é conectado.

Os scripts em `infra/postgres/init` usam PostgreSQL, não SQL Server. O workspace associa esses arquivos à linguagem `pgsql` para evitar diagnósticos incorretos da extensão MSSQL.

## API inicial

- `GET /health`
- `POST /api/v1/assets`
- `GET /api/v1/assets`
- `GET /api/v1/assets/{asset_id}`
- `POST /api/v1/assets/{asset_id}/locations`
- `GET /api/v1/assets/{asset_id}/locations`
- `POST /api/v1/gateway/signals` (entrada unificada para adaptadores MQTT/HTTPS)
- `POST /api/v1/ingest` (contrato público de ingestão)
- `GET /api/v1/devices/{identifier}` (IMEI, MAC ou telefone)
- `GET /api/v1/devices/{id}/last-location`
- `GET /api/v1/devices/{id}/history?from=...&to=...`
- `POST /api/v1/devices/{id}/geofence`
- `GET /api/v1/tracking/imei/{imei}` (última localização por IMEI)
- `GET /api/v1/tracking/mac/{mac_address}` (última localização por MAC)
- `GET /api/v1/tracking/cell/{cell_id}?tac={tac}` (torre celular ou última observação)
- `POST /api/v1/cell-towers` (cadastro/importação de torres)
- `POST /api/v1/wifi-access-points` (cadastro/importação de BSSIDs conhecidos)

### Enviar um sinal pelo Gateway

O gateway resolve o ativo a partir do identificador recebido e grava o evento de localização. O endpoint é compatível com adaptadores MQTT e HTTPS; o broker e o processador Kafka/RabbitMQ podem ser conectados sem alterar o contrato HTTP.

### API pública de ingestão

`POST /api/v1/ingest` aceita IMEI, MAC Address ou telefone no campo `identifier`, ou diretamente em `imei`, `mac_address` ou `phone_number`. Para GPS, envie `latitude` e `longitude`; para rede móvel sem GPS, envie `cell_id` e `tac` para resolução pela tabela `cell_towers`.

```json
{
  "phone_number": "+244923000000",
  "latitude": -8.8390,
  "longitude": 13.2894,
  "recorded_at": "2026-09-08T12:00:00Z"
}
```

Para desenvolvimento local, a migração inclui uma torre de demonstração em Luanda (`cell_id=10001`, `tac=100`) com coordenadas aproximadas `-8.8390, 13.2894` e precisão de 2,5 km. Essa referência deve ser substituída por dados reais de OpenCellID ou de outro provedor antes de produção.

### Métodos de rastreio

- IMEI e MAC procuram o dispositivo ativo e retornam o evento mais recente por `captured_at`.
- MAC com `wifi_fingerprint` consulta `wifi_access_points` e calcula uma posição ponderada pelo RSSI dos BSSIDs conhecidos.
- Cell ID/TAC consulta `cell_towers`; com várias observações em `cell_observations`, a API calcula uma posição ponderada pelo sinal. Sem GPS, retorna coordenadas aproximadas e `source: CELL_TOWER`.
- Quando já existe um evento por Cell ID/TAC, a resposta inclui esse evento e os dados da torre de referência.

Exemplo de fingerprint Wi-Fi:

```json
{
  "imei": "123456789012345",
  "wifi_fingerprint": [
    {"bssid": "AA:BB:CC:DD:EE:01", "signal_strength": -45},
    {"bssid": "AA:BB:CC:DD:EE:02", "signal_strength": -68}
  ],
  "recorded_at": "2026-09-08T12:00:00Z"
}
```

Exemplo de observação de múltiplas torres:

```json
{
  "imei": "123456789012345",
  "cell_observations": [
    {"cell_id": 10001, "tac": 100, "signal_strength": -70},
    {"cell_id": 10002, "tac": 100, "signal_strength": -82}
  ],
  "recorded_at": "2026-09-08T12:00:00Z"
}
```

```json
{
  "identifier": "268-01-12345-67890",
  "method": "cell_id",
  "cell_id": 12345,
  "tac": 678,
  "recorded_at": "2026-09-08T12:00:00Z"
}
```

O banco padrão é SQLite para desenvolvimento. Em produção, configure `DATABASE_URL` com PostgreSQL usando o driver `postgresql+asyncpg://...`.
