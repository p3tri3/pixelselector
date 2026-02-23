from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from pixelselector import PixelSelectorApp


def test_record_pixel_appends(app: PixelSelectorApp) -> None:
    app.image = Image.new("RGB", (100, 100))

    event = SimpleNamespace(x=10, y=20)
    app.record_pixel(event)  # type: ignore[arg-type]

    assert len(app.pixels) == 1
    assert app.pixels[0] == (10.0, 20.0)
    assert len(app.markers) == 1
    assert app.listbox.size() == 1


def test_record_pixel_multiple(app: PixelSelectorApp) -> None:
    app.image = Image.new("RGB", (100, 100))

    for x, y in [(1, 2), (3, 4), (5, 6)]:
        app.record_pixel(SimpleNamespace(x=x, y=y))  # type: ignore[arg-type]

    assert len(app.pixels) == 3
    assert len(app.markers) == 3
    assert app.listbox.size() == 3


def test_record_pixel_no_image(app: PixelSelectorApp) -> None:
    app.image = None
    event = SimpleNamespace(x=10, y=20)
    app.record_pixel(event)  # type: ignore[arg-type]
    assert app.pixels == []
    assert app.markers == []


def test_remove_pixel_syncs_state(app: PixelSelectorApp) -> None:
    app.pixels = [(10.0, 20.0), (30.0, 40.0)]
    app.update_markers()

    app.listbox.selection_set(0)
    app.remove_pixel()

    assert len(app.pixels) == 1
    assert len(app.markers) == 1
    assert app.listbox.size() == 1
    assert app.listbox.get(0).startswith("1:")


def test_remove_pixel_noop_without_selection(app: PixelSelectorApp) -> None:
    app.pixels = [(10.0, 20.0)]
    app.update_markers()
    app.listbox.selection_clear(0, "end")

    app.remove_pixel()

    assert len(app.pixels) == 1
    assert len(app.markers) == 1
    assert app.listbox.size() == 1


def test_update_markers_resets_all(app: PixelSelectorApp) -> None:
    app.pixels = [(10.0, 20.0), (30.0, 40.0)]
    app.markers = [99999]  # corrupt with a dummy canvas ID

    app.update_markers()

    assert len(app.markers) == 2
    assert all(isinstance(m, int) for m in app.markers)
    assert app.listbox.size() == 2
    assert app.listbox.get(0).startswith("1:")
    assert app.listbox.get(1).startswith("2:")


def test_drag_reorder_swaps_pixels(app: PixelSelectorApp) -> None:
    app.pixels = [(10.0, 20.0), (30.0, 40.0)]
    app.update_markers()

    app.listbox.selection_set(0)
    app.listbox.nearest = lambda y: 1  # type: ignore[method-assign]
    event = SimpleNamespace(y=999)

    app.drag_reorder(event)  # type: ignore[arg-type]

    assert app.pixels[0] == (30.0, 40.0)
    assert app.pixels[1] == (10.0, 20.0)


def test_drag_reorder_upward(app: PixelSelectorApp) -> None:
    app.pixels = [(10.0, 20.0), (30.0, 40.0)]
    app.update_markers()

    app.listbox.selection_set(1)
    app.listbox.nearest = lambda y: 0  # type: ignore[method-assign]
    event = SimpleNamespace(y=0)

    app.drag_reorder(event)  # type: ignore[arg-type]

    assert app.pixels[0] == (30.0, 40.0)
    assert app.pixels[1] == (10.0, 20.0)
    assert app.listbox.get(0).startswith("1:")
    assert app.listbox.get(1).startswith("2:")


def test_drag_reorder_same_index_noop(app: PixelSelectorApp) -> None:
    app.pixels = [(10.0, 20.0), (30.0, 40.0)]
    app.update_markers()
    initial_pixels = list(app.pixels)

    app.listbox.selection_set(0)
    app.listbox.nearest = lambda y: 0  # type: ignore[method-assign]
    event = SimpleNamespace(y=0)

    with patch.object(app, "update_markers") as mock_update:
        app.drag_reorder(event)  # type: ignore[arg-type]
        mock_update.assert_not_called()

    assert app.pixels == initial_pixels
