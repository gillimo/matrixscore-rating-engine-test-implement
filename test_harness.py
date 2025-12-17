import subprocess
import sys
import os

def run_test_harness():
    python_executable = r'C:\Users\gilli\AppData\Local\Programs\Python\Python39\python.exe'
    team_cli_script = 'team_cli_v5.py'
    demo_input_file = 'demo_input.txt'

    if not os.path.exists(python_executable):
        print(f"Error: Python executable not found at {python_executable}. Please update python_executable in test_harness.py", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(team_cli_script):
        print(f"Error: {team_cli_script} not found in the current directory.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(demo_input_file):
        print(f"Error: {demo_input_file} not found in the current directory.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(demo_input_file, 'r') as f:
            demo_input_content = f.read()

        print(f"Running '{team_cli_script}' in finalize mode...\n")
        
        process = subprocess.run(
            [python_executable, team_cli_script],
            input="finalize",
            text=True,
            capture_output=False,
            check=False
        )

        # Output is printed directly by team_cli_v3.py
        # Add a small delay to ensure all output is flushed before the script exits
        import time
        time.sleep(1) 

        # The actual error code might still be useful, though output is direct
        print(f"\n--- Test Harness finished (team_cli_v3.py exited with code {process.returncode}) ---")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    run_test_harness()
