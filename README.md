![welcome](https://github.com/etchedheadplate/area-bc1/blob/master/welcome.png)

[area bc1](https://t.me/area_bc1_bot) is a Telegram Bot to view Bitcoin-related statistics, make custom charts, explore blockchain and get regular notifications defined by user. Inspired by ideas of self-sovereignty and designed with love to Matt Stone, Trey Parker and Grey Visitors.

# Overview
### Bot
Bot uses `python-telegram-bot` as a wrapper for Telegram API.  All user commands in `bot.py`  have same name as files in `cmds/{module}.py`. Commands are available in private chats and groups, different command behavior executed using `update.effective_chat.type`. User input for notifications stored in `context.chat_data` and passed to `schedule`. Nested conversations in private chats use states. Bot uses `concurrent.futures` to run continuous database updates in separate thread and `asyncio` for notifications.
### Database
Database architecture described in `config.py`. Database initialized and updated regularly with `update_databases()` in `tools.py`. Data fetched from API providers (listed below) with `requests`. Chart data transferred to DataFrame with `pandas` and modified according to template specified in `config.py`. Files saved to `db/{command}/{command}` as `.json` or `.csv`. Regular database updates made by importing `cmds/{module}.py` with `importlib` to `schedule`.
### Images and text
Images and text made by `draw_{command}(day)` and  `write_{command}(day)` in `cmds/{module}.py`. Default day and image parameters defined in `config.py`. Plot data transferred to DataFrame with `pandas` and re-arranged with `numpy`. Lines and axes made with `matplotlib`. Image titles added with `pillows`. Image backgrounds are chosen from `src/image/backrounds/{module}_[down|up].png` with `define_key_metric_movement()` from `tools.py`. Text parsed from database files, direct API response or scraped and parsed with `beautifulsoup4`.  Text values formatted with various functions from `tools.py`. Files saved to `db/{command}/{command}_days_{day}` as `.jpg` or `.md`. User generated images and text removed with `clean_databases()` in `tools.py`

# Usage
```bash
pip3 install -r requirements.txt
python3 bot.py
```

# Known issues:
1. Some problems related to API data providers inconsistency:
    - Custom plot periods start date might not be precise because some API providers might not have history data for some days.
    - Lightning plot might miss data for some days from one update to another (self-corrects with database updates every ~2 hours).
    - CEX diagram might miss some exchanges from one update to another (self-corrects with database updates every ~15 minutes).
2. Functions for plot image generation use diffirent linewidth and rolling average for better user presentation, namely pandas `.rolling` method. Due to this method's behavior plot lines might not fully connect to plot borders.
3. User notifications are saved only in bot runtime and not stored in separate database for privacy reasons. In case of VPS instance imperfect uptime bot will be re-launched, and user should set notifications again manually.

# Acknowledgements
### Sources
This bot is powered by:
- [CoinGecko.com](https://www.coingecko.com/) API - Market, CEX
- [Mempool.Space](https://mempool.space/) API - Fees, Lightning, Pools
- [Blockchain.com](https://www.blockchain.com/) API - Blockchain, Market, Network
- [Coinqueror.io](https://coinqueror.io/) Data Scraping - News
- [Dune.com](https://dune.com/) API - ETFs, Seized
### Limitations
This bot uses free plans provided by API Sources. To comply with rate limits regular updates are throttled by periods specified in `config.py`.