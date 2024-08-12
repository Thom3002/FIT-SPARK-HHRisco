import os
import platform
import subprocess
import sys

venv_activate = r'c:\Users\thoma\Desktop\Spark\DevOps\FIT-SPARK-HHRisco\venv\Scripts\activate'
filepath = r"c:\Users\thoma\Desktop\Spark\DevOps\FIT-SPARK-HHRisco\src\util\prep_local_inst.py"
# command = r"activate; python c:\Users\thoma\Desktop\Spark\DevOps\FIT-SPARK-HHRisco\src\util\prep_local_inst.py"
command = f"{venv_activate}; python {filepath}"

result = subprocess.run(command, shell=True, text=True, capture_output=True)
if result.returncode != 0:
    print(f"Error running file {filepath}: {result.stderr}")
else:
    print(f"File {filepath} ran successfully.\nOutput:\n{result.stdout}")
