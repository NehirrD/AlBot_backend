import subprocess
import sys


def dev() -> None:
    result = subprocess.run(["uvicorn", "main:app", "--reload", "--app-dir", "src"])
    sys.exit(result.returncode)