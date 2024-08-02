This directory hosts media sources for bot frontend.

# Example Structure
```sh
src
├── font
│   ├── font1.ttf
│   ├── font2.ttf
│   └── ...
├── image
│   └── backgrounds
│       ├── background_for_{command1}.png
│       ├── background_for_{command2}_if_key_metric_is_up.png
│       ├── background_for_{command2}_if_key_metric_is_down.png
│       └── ...
└── text
    ├── about.md
    ├── hint_for_group_{command}.md
    ├── hint_for_nested_{command}.md
    └── ...
```

### Font

Files in this folder used for generating text on images. Font file path must be referenced in `images` dictionary of `config.py`. Files must have extentions supported by `PIL` library.

### Image

Files in this folder used for backrounds of generated images. Image file path must be referenced in `images` dictionary of `config.py`. Files must have extentions supported by `PIL` library.

### Text

Files in this folder used for markdown-formatted text messages. Text file path must be referenced in `cmds/{command}.py` in relevant functions. Files must have `.md` extention.