# Bybit Simple Assistant

API simple para:

- Consultar precio spot (`/price?symbol=BTCUSDT`)
- Ver balance (`/balance`)
- Crear orden spot de mercado (`POST /order`)

## Variables de entorno necesarias

- `BYBIT_API_KEY`
- `BYBIT_API_SECRET`
- `BYBIT_TESTNET` (`true` o `false`)

## Endpoints

- `GET /health`
- `GET /price?symbol=BTCUSDT`
- `GET /balance`
- `POST /order`

### Ejemplo de orden

POST `/order`

```json
{
  "symbol": "BTCUSDT",
  "side": "Buy",
  "qty": 0.001
}
