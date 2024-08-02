This directory hosts modules with bot commands.

# Example Structure
```sh
cmds
├── {command1}.py
├── {command2}.py
├── {command3}.py
├── ...
...
```

### Commands

Modules have names that corresponds to bot commands in back-end `bot.py` and front-end in user interface. Each module uses `draw_{command}()`, `write_{command}()` or both functions to process database data and generate output `.jpg` or `.md` file ready to be sent to user. If command requires number of days as argument, by default value is taken from `days` dictionary in `config.py`.

Data for images transferred from database to DataFrame with `pandas` and re-arranged with `numpy`. Lines and axes made with `matplotlib`. Image titles added with `PIL`. Image backgrounds are chosen with `define_key_metric_movement()` function from `tools.py`.

Data for texts transferred from database or scraped and parsed with `beautifulsoup4`. Text values modified with various formatting and conversion functions from `tools.py`.

Finally, generated images and texts are saved in `/db/{command}`