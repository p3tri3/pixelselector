from unittest.mock import MagicMock, patch

from pixelselector import PixelSelectorApp


def test_draw_marker_adds_to_markers(app: PixelSelectorApp) -> None:
    initial_count = len(app.markers)
    app.draw_marker(5.0, 10.0, 1)
    assert len(app.markers) == initial_count + 1
    assert isinstance(app.markers[-1], int)


def test_scroll_vertical_up(app: PixelSelectorApp) -> None:
    event = MagicMock()
    event.delta = 120
    with patch.object(app.canvas, "yview_scroll") as mock_scroll:
        app.scroll_vertical(event)
    mock_scroll.assert_called_once_with(-1, "units")


def test_scroll_vertical_down(app: PixelSelectorApp) -> None:
    event = MagicMock()
    event.delta = -120
    with patch.object(app.canvas, "yview_scroll") as mock_scroll:
        app.scroll_vertical(event)
    mock_scroll.assert_called_once_with(1, "units")


def test_scroll_horizontal_left(app: PixelSelectorApp) -> None:
    event = MagicMock()
    event.delta = 120
    with patch.object(app.canvas, "xview_scroll") as mock_scroll:
        app.scroll_horizontal(event)
    mock_scroll.assert_called_once_with(-1, "units")


def test_scroll_horizontal_right(app: PixelSelectorApp) -> None:
    event = MagicMock()
    event.delta = -120
    with patch.object(app.canvas, "xview_scroll") as mock_scroll:
        app.scroll_horizontal(event)
    mock_scroll.assert_called_once_with(1, "units")


def test_scroll_vertical_linux_up(app: PixelSelectorApp) -> None:
    event = MagicMock()
    event.num = 4
    with patch.object(app.canvas, "yview_scroll") as mock_scroll:
        app.scroll_vertical(event)
    mock_scroll.assert_called_once_with(-1, "units")


def test_scroll_vertical_linux_down(app: PixelSelectorApp) -> None:
    event = MagicMock()
    event.num = 5
    with patch.object(app.canvas, "yview_scroll") as mock_scroll:
        app.scroll_vertical(event)
    mock_scroll.assert_called_once_with(1, "units")
