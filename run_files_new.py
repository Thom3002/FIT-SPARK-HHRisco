import os
import platform
import subprocess
import sys


def run_python_file(filepath):
    """Run a Python file using subprocess within a virtual environment."""
    base_dir = os.path.dirname(filepath)
    venv_path = os.path.join(base_dir, 'venv')

    if platform.system() == "Windows":
        activate_script = 'activate'
        command = f"{activate_script}; python {filepath}"
    else:
        activate_script = os.path.join(venv_path, 'bin', 'activate')
        command = f"source {activate_script} && python {filepath}"

    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True,
                            text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error running file {filepath}: {result.stderr}")
    else:
        print(f"File {filepath} ran successfully.\nOutput:\n{result.stdout}")


def run_notebook_file(notebook_path):
    """Convert a Jupyter notebook to a Python script using nbconvert."""
    print(f"Converting notebook: {notebook_path}")

    # Definindo os caminhos da virtualenv
    base_dir = os.path.dirname(notebook_path)
    venv_path = os.path.join(base_dir, 'venv')
    activate_script = 'activate'
    jupyter_path = os.path.join(venv_path, 'Scripts', 'jupyter.exe')

    # Definindo o caminho do script de saída temporário
    temp_script_path = os.path.join(base_dir, os.path.splitext(
        os.path.basename(notebook_path))[0] + '.py')

    # Comando para converter o notebook
    command = f'{activate_script}; {jupyter_path} nbconvert --to python --output {temp_script_path} {notebook_path}'

    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"Notebook converted successfully.")
        run_python_file(temp_script_path)
        print("Rodou o arquivo: " + os.path.basename(temp_script_path))
    else:
        print(f"Error converting notebook: {result.stderr}")
        return None


def run_files_in_order(files):
    for file in files:
        if os.path.exists(file):
            print(f"Running file: {file}")
            if file.endswith('.py'):
                run_python_file(file)
            elif file.endswith('.ipynb'):
                run_notebook_file(file)
            else:
                print(f"Unsupported file type: {file}")
        else:
            print(f"File not found: {file}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    files_to_run = [
        # Parte pré-processamento local de instaçação (li)
        os.path.join(base_dir, 'src', 'util', 'prep_local_inst.py'),

        # Parte pré-processamento BD_acidentes
        os.path.join(base_dir, 'src', 'preprocessing',
                     'acidentes', 'preparacao.ipynb'),
        os.path.join(base_dir, 'src', 'preprocessing',
                     'acidentes', 'pre-processamento.ipynb'),
        os.path.join(base_dir, 'src', 'preprocessing',
                     'acidentes', 'agrupamento.ipynb'),

        # Parte pré-processamento os
        os.path.join(base_dir, 'src', 'preprocessing',
                     'os', 'preparacao.ipynb'),
        os.path.join(base_dir, 'src', 'preprocessing',
                     'os', 'agrupamento.ipynb')
    ]

    run_files_in_order(files_to_run)
