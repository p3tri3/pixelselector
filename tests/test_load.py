from unittest.mock import patch

from pixelselector import PixelSelectorApp


def test_load_image_sets_state(app: PixelSelectorApp, sample_image: str) -> None:
    app.load_image(sample_image)

    assert app.image is not None
    assert app.image_filename == "sample"
    assert app.pixels == []
    assert app.markers == []


def test_load_image_resets_previous_state(
    app: PixelSelectorApp, sample_image: str
) -> None:
    app.load_image(sample_image)
    app.pixels = [(1.0, 2.0)]
    app.update_markers()

    app.load_image(sample_image)

    assert app.pixels == []
    assert app.markers == []
    assert app.listbox.size() == 0


def test_load_image_dialog_cancelled(app: PixelSelectorApp) -> None:
    app.image = None
    app.image_filename = ""

    with patch("tkinter.filedialog.askopenfilename", return_value=""):
        app.load_image()

    assert app.image is None
    assert app.image_filename == ""
