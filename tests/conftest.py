import tkinter as tk
from collections.abc import Generator
from pathlib import Path

import pytest
from PIL import Image

from pixelselector import PixelSelectorApp


@pytest.fixture(scope="session")
def tk_root() -> Generator[tk.Tk, None, None]:
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def app(tk_root: tk.Tk) -> Generator[PixelSelectorApp, None, None]:
    instance = PixelSelectorApp(tk_root)
    yield instance
    instance.image_frame.destroy()
    instance.list_frame.destroy()


@pytest.fixture
def sample_image(tmp_path: Path) -> Generator[str, None, None]:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    path = tmp_path / "sample.png"
    img.save(path)
    yield str(path)
