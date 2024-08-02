![welcome](https://github.com/etchedheadplate/area-bc1/blob/master/welcome.png)

[area bc1](https://t.me/area_bc1_bot) is a Telegram Bot to view Bitcoin-related statistics, make custom charts, explore blockchain and get regular notifications defined by user. Inspired by ideas of self-sovereignty and designed with love to Matt Stone, Trey Parker and Grey Visitors.

# Workflow

This bot implemented as a Finite‑State Machine with states and uses `python-telegram-bot` library as a wrapper for Telegram API. All commands are available in private chats and groups. Some commands support nested conversations in private chats, different command behavior executed using `update.effective_chat.type`. User input for notifications stored in `context.chat_data` and executed with `schedule`. Bot uses `concurrent.futures` to run continuous database maintenance and `asyncio` for notifications.

Additional information on commands, database and source media files can be found in README.md of corresponding directories.

# Deployment

```sh
pip3 install -r requirements.txt
python3 bot.py
```

# Known issues:

1. Due to API source data inconsistency some charts may miss data for given day. Usually this issue self-corrects with next database update.
2. Functions for plot image generation use diffirent linewidth and rolling average for better user presentation, namely pandas `.rolling` method. Due to this method's behavior plot lines might not fully connect to plot borders.
3. User notifications are saved only in bot runtime and not stored in separate database for privacy reasons. In case of VPS instance imperfect uptime bot will be re-launched, and user should set notifications again manually.

# Acknowledgements

### Sources
This bot is powered by:
- [CoinGecko.com](https://www.coingecko.com/) API - Market, CEX
- [Mempool.Space](https://mempool.space/) API - Fees, Lightning, Pools
- [Blockchain.com](https://www.blockchain.com/) API - Blockchain, Market, Network
- [Coinqueror.io](https://coinqueror.io/) data scraping - News
- [Dune.com](https://dune.com/) API - ETFs, Seized

### Limitations
This bot uses free plans provided by API Sources. To comply with rate limits regular updates are throttled by periods specified in `config.py`.