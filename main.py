from fastapi import FastAPI, Query
import MetaTrader5 as mt5
from fastapi.responses import JSONResponse

app = FastAPI()

TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
    "W1": mt5.TIMEFRAME_W1,
    "MN1": mt5.TIMEFRAME_MN1
}


@app.get("/tick/{symbol}")
def get_symbol_tick(symbol: str):
    mt5.initialize()
    tick = mt5.symbol_info_tick(symbol)
    mt5.shutdown()
    return {
        "bid": tick.bid,
        "ask": tick.ask,
        "last": tick.last
    }


@app.get("/symbols")
def get_symbols():
    mt5.initialize()
    symbols = mt5.symbols_get()
    active_symbols = [(s.name, s.description, s.session_open, s.session_close, s.isin, s.path) for s in symbols if s.trade_mode==4]
    mt5.shutdown()
    return active_symbols


@app.get("/symbols-invest")
def get_symbols_invest():
    mt5.initialize()
    symbols = mt5.symbols_get()
    active_symbols = [(s.name, s.description, s.session_open, s.session_close, s.isin, s.path) for s in symbols if s.trade_mode==1]
    mt5.shutdown()
    return active_symbols


@app.get("/symbol-info/{symbol}")
def get_symbol_info(symbol: str):
    mt5.initialize()
    symbol_info = mt5.symbol_info(symbol)._asdict()
    mt5.shutdown()
    return symbol_info


@app.get("/symbol-select/{symbol}")
def symbol_select(symbol: str):
    mt5.initialize()
    symbol_select = mt5.symbol_select(symbol)
    mt5.shutdown()
    return f'{symbol_select} added to mt5 terminal'


@app.get("/price-history/{symbol}")
def get_price_history(symbol: str, timeframe: str = Query(default="TIMEFRAME_D1"), count: int = 100):
    mt5.initialize()

    tf = TIMEFRAME_MAP.get(timeframe, mt5.TIMEFRAME_D1)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        return {"error": f"No price data for {symbol} at {timeframe}."}

    clean_data = []
    for row in rates:
        clean_data.append({
            "time": int(row["time"]),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "tick_volume": int(row["tick_volume"]),
        })

    return clean_data


@app.get("/ping")
def ping():
    mt5.initialize()
    info = mt5.account_info()._asdict()
    leverage = info['leverage']
    if leverage != 1:
        account = 'trade'
    else:
        account = 'invest'
    mt5.shutdown()
    return account


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)


