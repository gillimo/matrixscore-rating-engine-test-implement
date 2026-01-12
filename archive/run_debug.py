import subprocess
import sys
import os

# Get the directory where run_debug.py is located
script_dir = os.path.dirname(os.path.realpath(__file__))
team_cli_path = os.path.join(script_dir, 'team_cli_v3.py')

try:
    # Use the specific python executable if it's known, otherwise sys.executable
    # From SYSTEM_NOTES.md: Python 3.9 at `C:\Users\gilli\AppData\Local\Programs\Python\Python39\python.exe`
    python_executable = r'C:\Users\gilli\AppData\Local\Programs\Python\Python39\python.exe'
    
    result = subprocess.run([python_executable, team_cli_path, '--help'], capture_output=True, text=True, check=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Subprocess failed with exit code:", e.returncode)
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
except Exception as e:
    print("An unexpected error occurred:", e)

