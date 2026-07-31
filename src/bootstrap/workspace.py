from pathlib import Path
import sys


def register_workspace_src() -> Path:
    """
    Register the project's src directory.

    Searches upward from the current working directory
    until it finds the repository root containing 'src'.
    """

    current = Path.cwd()

    while current != current.parent:

        candidate = current / "src"

        if candidate.exists():

            src_path = str(candidate)

            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            return candidate

        current = current.parent

    raise RuntimeError(
        "Unable to locate project src directory."
    )