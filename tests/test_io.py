import json
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from pixelselector import PixelSelectorApp


def test_save_json_creates_file(
    app: PixelSelectorApp,
    sample_image: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app.load_image(sample_image)
    app.pixels = [(10.0, 20.0), (30.0, 40.0)]
    monkeypatch.chdir(tmp_path)
    with patch("tkinter.messagebox.showinfo"):
        app.save_json()
    json_file = tmp_path / "sample_pixels.json"
    assert json_file.exists()
    data = json.loads(json_file.read_text())
    assert "pixels" in data
    assert data["pixels"] == [[10.0, 20.0], [30.0, 40.0]]


def test_save_json_noop_without_image(
    app: PixelSelectorApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app.image_filename = ""
    monkeypatch.chdir(tmp_path)
    app.save_json()
    assert list(tmp_path.glob("*.json")) == []


def test_export_image_creates_file(
    app: PixelSelectorApp,
    sample_image: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app.load_image(sample_image)
    app.pixels = [(5.0, 5.0)]
    monkeypatch.chdir(tmp_path)
    with patch("tkinter.messagebox.showinfo"):
        app.export_image()
    png_file = tmp_path / "sample_reference.png"
    assert png_file.exists()
    img = Image.open(png_file)
    assert img.format == "PNG"


def test_export_image_noop_without_image(
    app: PixelSelectorApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app.image_filename = ""
    app.image = None
    monkeypatch.chdir(tmp_path)
    app.export_image()
    assert list(tmp_path.glob("*.png")) == []


def test_export_image_zero_pixels(
    app: PixelSelectorApp,
    sample_image: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app.load_image(sample_image)
    app.pixels = []
    monkeypatch.chdir(tmp_path)
    with patch("tkinter.messagebox.showinfo"):
        app.export_image()
    png_file = tmp_path / "sample_reference.png"
    assert png_file.exists()
    img = Image.open(png_file)
    assert img.format == "PNG"


def test_quick_save_calls_both(app: PixelSelectorApp) -> None:
    with (
        patch.object(app, "save_json") as mock_save,
        patch.object(app, "export_image") as mock_export,
    ):
        app.quick_save()
    mock_save.assert_called_once()
    mock_export.assert_called_once()
