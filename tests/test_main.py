import subprocess
import sys
from pathlib import Path


def test_main_block() -> None:
    pixelselector = Path(__file__).parent.parent / "pixelselector.py"
    code = (
        "import tkinter as tk; "
        "tk.Tk.mainloop = lambda self: None; "
        f"import runpy; runpy.run_path({str(pixelselector)!r}, run_name='__main__')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
