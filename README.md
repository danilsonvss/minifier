# minifier

## Dependências
YUI Compressor - https://yui.github.io/yuicompressor

## Building

```
pyinstaller --onefile --add-data "yuicompressor-2.4.8.jar:." minifier.py
```

## Opções Disponíveis
1. `-d, --directory`: Especifica o diretório a ser pesquisado para arquivos CSS e JS ou para observação de alterações.
1. `-f, --files`: Lista de arquivos específicos a serem minificados (separados por vírgula).
1. `-e, --encoding`: Define o encoding para a minificação dos arquivos (default é utf-8).
1. `-w, --watch`: Ativa o modo de observação para detectar alterações e minificar automaticamente os arquivos.
