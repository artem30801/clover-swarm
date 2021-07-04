import sys
from subprocess import CalledProcessError, check_call


def run_process(args, shell=False):
    """Run program provided by args.

    Return True on success.
    Output failed message on non-zero exit and return False.
    Return False if command is not found.
    """
    command = " ".join(args)
    print(f"Running: {command}")
    try:
        check_call(args, shell=shell)
    except CalledProcessError:
        print(f"Failed: {command}")
        return False
    except Exception as exc:
        sys.stderr.write(f"{str(exc)}\n")
        return False
    return True


def run_static():
    """Runs static tests.

    Returns a statuscode of 0 if everything ran correctly. Otherwise, it will return
    statuscode 1

    """
    success = True
    # Formatters
    success &= run_process(["black", "."])
    success &= run_process(["isort", "."])
    # Linters
    success &= run_process(["flake8", "--exclude=.eggs,build,docs,.venv*", "--max-line-length=100"])

    return success


def main():
    try:
        success = run_static()
    except KeyboardInterrupt:
        return 1
    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print(f"pre_push.py: {'Success!' if not exit_code else 'Fail'}")
    sys.exit(exit_code)
