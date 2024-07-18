import os
import subprocess
import argparse
import sys
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Caminho para o arquivo yuicompressor
if hasattr(sys, '_MEIPASS'):
    YUI_COMPRESSOR_PATH = os.path.join(sys._MEIPASS, 'yuicompressor-2.4.8.jar')
else:
    YUI_COMPRESSOR_PATH = 'yuicompressor-2.4.8.jar'

# Caminho para o arquivo de configuração
CONFIG_DIR_PATH = '.vscode'
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'config.json')

# Função para carregar configurações
def load_config():
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    return {}

# Função para salvar configurações
def save_config(config):
    os.makedirs(CONFIG_DIR_PATH, exist_ok=True)
    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file, ensure_ascii=False)

# Função para minificar um arquivo usando YUI Compressor
def minify_file(file_path, encoding):
    if not file_path.endswith(('.css', '.js')):
        return
    
    # Obtém o diretório e o nome do arquivo sem extensão
    directory = os.path.dirname(file_path)
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    
    # Cria o nome do arquivo minificado
    minified_file_path = os.path.join(directory, f"{base_filename}.min{os.path.splitext(file_path)[1]}")

    # Verifica se o arquivo minificado já existe
    if os.path.exists(minified_file_path):
        return

    # Ler conteúdo do arquivo usando o encoding especificado
    with open(file_path, 'r', encoding=encoding) as original_file:
        original_content = original_file.read()

    # Comando para minificar o arquivo
    command = [
        'java', '-jar', YUI_COMPRESSOR_PATH,
        '--type', os.path.splitext(file_path)[1].lstrip('.'),
        '--charset', encoding,
        '-o', minified_file_path,
    ]

    # Executa o comando com o conteúdo do arquivo original
    subprocess.run(command, input=original_content.encode(encoding), check=True)

# Função para minificar arquivos especificados
def minify_specified_files(file_paths, encoding):
    for file_path in file_paths:
        if os.path.isfile(file_path):
            minify_file(file_path, encoding)
        else:
            print(f"Arquivo não encontrado: {file_path}")

# Classe para lidar com eventos de modificação de arquivo
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, encoding):
        super().__init__()
        self.encoding = encoding

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(('.js', '.css')) or event.src_path.endswith(('.min.js', '.min.css')):
            return
        
        minify_file(event.src_path, self.encoding)
        print(f"Arquivo modificado: {event.src_path}")

# Função para iniciar o monitoramento de diretório
def start_watch(directory, encoding):
    event_handler = FileChangeHandler(encoding)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    print(f"Observando alterações em {directory}... Pressione Ctrl+C para parar.")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Carregar configurações
    config = load_config()
    default_encoding = config.get('default_encoding', 'utf-8')

    # Configura o argparse para aceitar o diretório, encoding e arquivos como argumentos
    parser = argparse.ArgumentParser(description="Minify CSS and JS files using YUI Compressor")
    parser.add_argument("-d", "--directory", help="The directory to search for CSS and JS files")
    parser.add_argument("-f", "--files", help="Comma-separated list of specific files to minify")
    parser.add_argument("-e", "--encoding", default=default_encoding, help="The encoding to use for minification (default is utf-8)")
    parser.add_argument("-w", "--watch", action="store_true", help="Watch for file changes in the specified directory and automatically minify")

    args = parser.parse_args()

    # Atualiza o encoding padrão nas configurações se necessário
    if args.encoding != default_encoding:
        config['default_encoding'] = args.encoding
        save_config(config)

    # Minificar arquivos especificados se --files ou -f estiver presente
    if args.files:
        file_paths = [f.strip() for f in args.files.split(',') if f.strip()]
        minify_specified_files(file_paths, args.encoding)
    elif args.directory or args.d:
        directory = args.directory or args.d
        # Verifica se o diretório existe
        if not os.path.isdir(directory):
            print(f"Erro: O diretório {directory} não existe.")
            exit(1)

        # Se o modo de observação estiver ativado
        if args.watch:
            start_watch(directory, args.encoding)
        else:
            # Percorre o diretório fornecido e minifica os arquivos CSS e JS
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    minify_file(file_path, args.encoding)
    else:
        print("É necessário especificar -d ou --directory para um diretório ou -f ou --files para arquivos específicos.")
        exit(1)
