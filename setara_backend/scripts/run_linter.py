import subprocess
import sys


def main():  # pragma: no cover
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "autopep8",
            "--in-place",
            "--recursive",
            "setara_backend/"
        ])
    except subprocess.CalledProcessError as e:
        print(f"Autoformatting failed with error code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":  # pragma: no cover
    main()
