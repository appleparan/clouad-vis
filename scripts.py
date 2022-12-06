import subprocess


def test():
    """
    Run all unittests. Equivalent to:
    `poetry run python -u -m unittest discover`
    """
    subprocess.Popen(["python", "-m", "pytest", "--import-mode=importlib"])


def lint():
    """
    Run all unittests. Equivalent to:
    `poetry run python -u -m unittest discover`
    """
    subprocess.Popen(["pylint", ".", " --rcfile=.pylintrc"])
