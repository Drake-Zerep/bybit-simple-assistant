import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# Cargar variables de entorno (útil en local; en Render también funciona)
load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
USE_TESTNET = os.getenv("BYBIT_TESTNET", "false").lower() == "true"

if not API_KEY or not API_SECRET:
    # No rompemos la app, pero avisamos en logs
    print("⚠️ Falta BYBIT_API_KEY o BYBIT_API_SECRET en variables de entorno")

# Sesión con Bybit Unified Trading
session = HTTP(
    testnet=USE_TESTNET,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

app = FastAPI(
    title="Bybit Simple Assistant",
    description="API simple para consultar precio, balance y crear órdenes spot de mercado en Bybit.",
    version="0.1.0",
)


class OrderRequest(BaseModel):
    symbol: str      # Ej: "BTCUSDT"
    side: str        # "Buy" o "Sell"
    qty: float       # Ej: 0.001


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/price")
def get_price(symbol: str):
    """
    Devuelve precio actual de un símbolo spot (ej: BTCUSDT).
    """
    try:
        data = session.get_tickers(category="spot", symbol=symbol)
        result = data.get("result", {}).get("list", [])
        if not result:
            raise HTTPException(status_code=404, detail="Símbolo no encontrado o sin datos")

        ticker = result[0]
        return {
            "symbol": symbol,
            "lastPrice": ticker.get("lastPrice"),
            "bid1Price": ticker.get("bid1Price"),
            "ask1Price": ticker.get("ask1Price"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener precio: {e}")


@app.get("/balance")
def get_balance():
    """
    Devuelve balances de la cuenta (Unified).
    """
    try:
        data = session.get_wallet_balance(accountType="UNIFIED")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener balance: {e}")


@app.post("/order")
def place_order(order: OrderRequest):
    """
    Crea una orden spot de mercado.
    """
    side = order.side.capitalize()
    if side not in ["Buy", "Sell"]:
        raise HTTPException(status_code=400, detail="side debe ser 'Buy' o 'Sell'")

    try:
        resp = session.place_order(
            category="spot",
            symbol=order.symbol,
            side=side,
            orderType="Market",
            qty=str(order.qty),
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear orden: {e}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "10000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
