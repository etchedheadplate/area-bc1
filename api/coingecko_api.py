API_ERROR_CODES = {
    400:"Bad Request",
    403:"Forbidden",
    404:"test",
    401:"Unauthorised",
    429:"Too many requests",
    500:"Internal Server Error",
    503:"Service Unavailable",
    1020:"Acces Denied",
    10002:"API Key Missing",
    10005:"Request limited to PRO API"
}

API_ENDPOINTS = {
    "/simple/price":"Get the current price of any cryptocurrencies in any other supported currencies that you need.",
    "/simple/token_price/{id}":"Get current price of tokens (using contract addresses) for a given platform in any other currency that you need.",
    "/simple/supported_vs_currencies":"Get list of supported_vs_currencies.",
    "/coins/list":"List all supported coins id, name and symbol (no pagination required)",
    "/coins/markets":"List all supported coins price, market cap, volume, and market related data",
    "/coins/{id}":"Get current data (name, price, market, ... including exchange tickers) for a coin",
    "/coins/{id}/tickers":"Get coin tickers (paginated to 100 items)",
    "/coins/{id}/history":"Get historical data (price, market cap, 24hr volume, ..) at a given date for a coin.",
    "/coins/{id}/market_chart":"Get historical market data include price, market cap, and 24h volume (granularity auto)",
    "/coins/{id}/market_chart/range":"Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto)",
    "/coins/{id}/ohlc":"Get coin's OHLC",
    "/coins/{id}/contract/{contract_address}":"Get coin info from contract address",
    "/coins/{id}/contract/{contract_address}/market_chart/":"Get historical market data include price, market cap, and 24h volume (granularity auto) from a contract address" ,
    "/coins/{id}/contract/{contract_address}/market_chart/range":"Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto) from a contract address",
    "/asset_platforms":"List all asset platforms (Blockchain networks)",
    "/coins/categories/list":"List all categories",
    "/coins/categories":"List all categories with market data",
    "/exchanges":"List all exchanges (Active with trading volumes)",
    "/exchanges/list":"List all supported markets id and name (no pagination required)",
    "/exchanges/{id}":"Get exchange volume in BTC and top 100 tickers only",
    "/exchanges/{id}/tickers":"Get exchange tickers (paginated, 100 tickers per page)",
    "/exchanges/{id}/volume_chart":"Get volume_chart data (in BTC) for a given exchange",
    "/derivatives":"List all derivative tickers",
    "/derivatives/exchanges":"List all derivative exchanges",
    "/derivatives/exchanges/{id}":"show derivative exchange data",
    "/derivatives/exchanges/list":"List all derivative exchanges name and identifier",
    "/nfts/list":"List all supported NFT ids, paginated by 100 items per page, paginated to 100 items",
    "/nfts/{id}":"Get current data (name, price_floor, volume_24h ...) for an NFT collection",
    "/nfts/{asset_platform_id}/contract/{contract_address}":"Get current data (name, price_floor, volume_24h ...) for an NFT collection.",
    "/exchange_rates":"Get BTC-to-Currency exchange rates",
    "/search":"Search for coins, categories and markets on CoinGecko",
    "/search/trending":"Get trending search coins (Top-7) on CoinGecko in the last 24 hours",
    "/global":"Get cryptocurrency global data",
    "/global/decentralized_finance_defi":"Get cryptocurrency global decentralized finance(defi) data",
    "/companies/public_treasury/{id}":"Get public companies data"
}

ID = "bitcoin"

'''BITCOIN = {
    "id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin"
}'''