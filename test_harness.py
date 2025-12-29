import argparse
import subprocess
import sys
from pathlib import Path


def run_test_harness():
    """
    Run team_cli_v6.py and surface its output directly.
    By default, sends a single "finalize" command so you can see the autofill output.
    """
    parser = argparse.ArgumentParser(description="Simple harness to exercise team_cli_v6.py and view output.")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter to use (defaults to current).")
    parser.add_argument("--script", default="team_cli_v6.py", help="Target CLI script.")
    parser.add_argument(
        "--commands",
        default="finalize",
        help="Command string to feed to stdin (use \\n to separate lines). Default: finalize.",
    )
    parser.add_argument(
        "--input-file",
        default=None,
        help="Optional path to a file whose contents will be piped to stdin instead of --commands.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    python_executable = Path(args.python)
    team_cli_script = repo_root / args.script

    if not python_executable.exists():
        print(f"Error: Python executable not found at {python_executable}", file=sys.stderr)
        sys.exit(1)

    if not team_cli_script.exists():
        print(f"Error: {team_cli_script} not found.", file=sys.stderr)
        sys.exit(1)

    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)
        input_payload = input_path.read_text()
        input_source = f"file:{input_path.name}"
    else:
        input_payload = args.commands
        input_source = "commands"

    if not input_payload.endswith("\n"):
        input_payload += "\n"

    print(f"Running {team_cli_script.name} via {python_executable} using stdin from {input_source}...\n")

    process = subprocess.run(
        [str(python_executable), str(team_cli_script)],
        input=input_payload,
        text=True,
        capture_output=False,
        check=False,
        cwd=repo_root,
    )

    print(f"\n--- Harness finished (exit code {process.returncode}) ---")


if __name__ == "__main__":
    run_test_harness()
