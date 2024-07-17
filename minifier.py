import os
import subprocess
import argparse
import sys

# Caminho para o arquivo yuicompressor
if hasattr(sys, '_MEIPASS'):
    YUI_COMPRESSOR_PATH = os.path.join(sys._MEIPASS, 'yuicompressor-2.4.8.jar')
else:
    YUI_COMPRESSOR_PATH = 'yuicompressor-2.4.8.jar'

# Função para minificar um arquivo usando YUI Compressor
def minify_file(file_path):
    minified_file_path = f"{file_path}.min"

    # Comando para minificar o arquivo
    command = [
        'java', '-jar', YUI_COMPRESSOR_PATH,
        file_path, '-o', minified_file_path
    ]

    # Executa o comando
    subprocess.run(command, check=True)

    # Substitui o arquivo original pelo minificado
    os.replace(minified_file_path, file_path)

# Função para percorrer diretórios e minificar arquivos CSS e JS
def minify_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.css', '.js')):
                file_path = os.path.join(root, file)
                print(f"Minificando {file_path}...")
                minify_file(file_path)

if __name__ == "__main__":
    # Configura o argparse para aceitar o diretório como argumento
    parser = argparse.ArgumentParser(description="Minify CSS and JS files using YUI Compressor")
    parser.add_argument("directory", help="The directory to search for CSS and JS files")

    args = parser.parse_args()

    # Verifica se o diretório existe
    if not os.path.isdir(args.directory):
        print(f"Erro: O diretório {args.directory} não existe.")
        exit(1)

    # Minifica os arquivos no diretório fornecido
    minify_directory(args.directory)
