import os
import platform
import subprocess
import sys

current_directory = []


def run_python_file(filepath):
    """Run a Python file using subprocess."""
    print(f"Running file: {filepath}")
    result = subprocess.run(['python', filepath])
    if result.returncode != 0:
        print(f"Error running file {filepath}: {result.stderr}")


def convert_notebook_to_python(notebook_path):
    """Convert a Jupyter notebook to a Python script using nbconvert."""
    print(f"Converting notebook: {notebook_path}")
    temp_script_path = 'temp-nb-to-python.py'

    global current_directory
    current_directory = notebook_path.split("/")[:-1]

    result = subprocess.run(['jupyter', 'nbconvert', '--to',
                            'python', '--output', temp_script_path, notebook_path])
    if result.returncode == 0:
        return temp_script_path
    else:
        print(f"Error converting notebook: {result.stderr}")
        return None


def run_notebook_file(notebook_path):
    """Convert a Jupyter notebook to a Python file and run it."""
    temp_script_path = convert_notebook_to_python(notebook_path)
    if temp_script_path:
        path_to_cd = "/".join(current_directory) + "/"
        os.chdir(path_to_cd)
        run_python_file(temp_script_path)
        os.remove(temp_script_path)
        os.chdir("../" * len(current_directory))


def run_files_in_order(files):
    """Run a list of files in the specified order."""
    for file in files:
        if not os.path.isfile(file):
            print(f"File does not exist: {file}")
            raise FileNotFoundError
        if file.endswith('.py'):
            run_python_file(file)
        elif file.endswith('.ipynb'):
            run_notebook_file(file)
        else:
            print(f"Unsupported file type: {file}")


def create_virtualenv(env_path):
    """Create a virtual environment."""
    print(f"Creating virtual environment at {env_path}")
    subprocess.run([sys.executable, '-m', 'venv', env_path], check=True)
    print("Virtual environment created.")


def install_dependencies(env_path):
    """Install dependencies using pip."""
    pip_executable = os.path.join(env_path, 'Scripts', 'pip.exe') if platform.system(
    ) == "Windows" else os.path.join(env_path, 'bin', 'pip')
    print("Installing dependencies...")
    subprocess.run([pip_executable, 'install', '-r',
                   'requirements.txt'], check=True)
    print("Dependencies installed.")


def get_activate_command():
    """Get the command to activate the virtual environment."""
    env_path = os.path.join(os.getcwd(), 'venv')
    if platform.system() == "Windows":
        return os.path.join(env_path, 'Scripts', 'activate.bat')
    else:
        return f"source {os.path.join(env_path, 'bin', 'activate')}"


if __name__ == "__main__":
    files_to_run = [
        # Parte pré-processamento local de instaçação (li)
        'src/util/prep_local_inst.py',

        # Parte pré-processamento BD_acidentes
        'src/preprocessing/acidentes/preparacao.ipynb',
        'src/preprocessing/acidentes/pre-processamento.ipynb',
        'src/preprocessing/acidentes/agrupamento.ipynb',

        # Parte pré-processamento os
        'src/preprocessing/os/preparacao.ipynb',
        'src/preprocessing/os/agrupamento.ipynb'
    ]

    env_path = os.path.join(os.getcwd(), 'venv')

    if not os.path.exists(env_path):
        create_virtualenv(env_path)
        install_dependencies(env_path)
    else:
        print(f"Virtual environment already exists at {env_path}")

    activate_command = get_activate_command()

    # Run files in the specified order within the virtual environment
    for file in files_to_run:
        if file.endswith('.py'):
            subprocess.run(f"{activate_command} && python {file}", shell=True)
        elif file.endswith('.ipynb'):
            temp_script_path = convert_notebook_to_python(file)
            if temp_script_path:
                subprocess.run(
                    f"{activate_command} && python {temp_script_path}", shell=True)
                os.remove(temp_script_path)
        else:
            print(f"Unsupported file type: {file}")
