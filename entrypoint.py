import subprocess
import sys
import uvicorn


def run_migrations() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=False,
    )
    if result.returncode != 0:
        print("falha ao rodar as migrations.", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    run_migrations()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
