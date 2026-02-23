import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageDraw, ImageFont, ImageTk


class PixelSelectorApp:
    """Tkinter GUI for selecting and recording pixel coordinates on an image.

    State contract: ``self.pixels`` is the single source of truth for recorded
    coordinates.  ``self.markers`` (canvas item IDs) and the Listbox are always
    derived from ``self.pixels`` and kept in sync by ``update_markers``.

    Output files are written to the working directory using the stem of the
    loaded filename:
    - ``{stem}_pixels.json``     — ``{"pixels": [[x, y], ...]}``
    - ``{stem}_reference.png``   — copy of the image annotated with red labels
    """

    def __init__(self, root: tk.Tk, image_path: str | None = None) -> None:
        """Build the UI and optionally load an image from *image_path*."""
        self.root = root
        self.root.title("Pixel Selector Tool")
        self.image_filename: str = ""

        # Menu
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Image", command=self.load_image)
        file_menu.add_command(label="Save JSON", command=self.save_json)
        file_menu.add_command(label="Export Marked Image", command=self.export_image)
        file_menu.add_command(label="Quick Save", command=self.quick_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        # Image Frame with Scrollbars
        self.image_frame = tk.Frame(root)
        self.image_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.image_frame)
        self.scroll_x = tk.Scrollbar(
            self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.scroll_y = tk.Scrollbar(
            self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )

        self.canvas.configure(
            xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set
        )

        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.canvas.bind("<Button-1>", self.record_pixel)
        self.canvas.bind("<MouseWheel>", self.scroll_vertical)
        self.canvas.bind("<Button-4>", self.scroll_vertical)
        self.canvas.bind("<Button-5>", self.scroll_vertical)
        self.canvas.bind("<Shift-Control-MouseWheel>", self.scroll_horizontal)

        # Pixel List Frame
        self.list_frame = tk.Frame(root)
        self.list_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.listbox = tk.Listbox(self.list_frame, height=20, width=20)
        self.listbox.pack()

        self.listbox.bind("<B1-Motion>", self.drag_reorder)
        self.listbox.bind("<Delete>", lambda _: self.remove_pixel())

        self.remove_button = tk.Button(
            self.list_frame, text="Remove Selected", command=self.remove_pixel
        )
        self.remove_button.pack(pady=5)

        self.pixels: list[tuple[float, float]] = []
        self.markers: list[int] = []
        self.image: Image.Image | None = None
        self.tk_image: ImageTk.PhotoImage | None = None
        self.canvas_image_id: int | None = None

        if image_path:
            self.load_image(image_path)

    def scroll_vertical(self, event: tk.Event[tk.Canvas]) -> None:
        """Scroll the canvas vertically on mouse-wheel or Linux Button-4/5 events."""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")

    def scroll_horizontal(self, event: tk.Event[tk.Canvas]) -> None:
        """Scroll the canvas horizontally on Shift-Ctrl-mouse-wheel events."""
        direction = -1 if event.delta > 0 else 1
        self.canvas.xview_scroll(direction, "units")

    def load_image(self, file_path: str | None = None) -> None:
        """Load an image from *file_path*, or open a file dialog if omitted."""
        if file_path is None:
            file_path = filedialog.askopenfilename(
                filetypes=[("PNG Images", "*.png"), ("All Files", "*.*")]
            )
        if file_path:
            self.image = Image.open(file_path).convert("RGB")
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.config(scrollregion=(0, 0, self.image.width, self.image.height))
            if self.canvas_image_id is not None:
                self.canvas.delete(self.canvas_image_id)
            self.canvas_image_id = self.canvas.create_image(
                0, 0, anchor=tk.NW, image=self.tk_image
            )
            self.pixels.clear()
            self.listbox.delete(0, tk.END)
            self.markers.clear()
            self.image_filename = os.path.splitext(os.path.basename(file_path))[0]

    def record_pixel(self, event: tk.Event[tk.Canvas]) -> None:
        """Append the clicked canvas coordinate to ``self.pixels`` and draw a marker."""
        if self.image is None:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.pixels.append((x, y))
        self.listbox.insert(tk.END, f"{len(self.pixels)}: ({x}, {y})")
        self.draw_marker(x, y, len(self.pixels))

    def draw_marker(self, x: float, y: float, number: int) -> None:
        """Draw a numbered red text marker on the canvas at *(x, y)*."""
        marker = self.canvas.create_text(
            x, y, text=str(number), fill="red", font=("Arial", 12, "bold")
        )
        self.markers.append(marker)

    def update_markers(self) -> None:
        """Redraw all canvas markers and rebuild the Listbox from ``self.pixels``."""
        for item in self.markers:
            self.canvas.delete(item)
        self.markers.clear()
        self.listbox.delete(0, tk.END)
        for i, (x, y) in enumerate(self.pixels):
            self.listbox.insert(tk.END, f"{i + 1}: ({x}, {y})")
            self.draw_marker(x, y, i + 1)

    def remove_pixel(self) -> None:
        """Remove the currently selected pixel and refresh markers."""
        selected_idx = self.listbox.curselection()  # type: ignore[no-untyped-call]
        if not selected_idx:
            return
        self.pixels.pop(selected_idx[0])
        self.update_markers()

    def drag_reorder(self, event: tk.Event[tk.Listbox]) -> None:
        """Reorder pixels by dragging a Listbox entry to a new position."""
        selected = self.listbox.curselection()  # type: ignore[no-untyped-call]
        if not selected:
            return
        idx = selected[0]
        new_idx = self.listbox.nearest(event.y)  # type: ignore[no-untyped-call]
        if idx != new_idx:
            self.pixels.insert(new_idx, self.pixels.pop(idx))
            self.update_markers()

    def save_json(self) -> None:
        """Save ``self.pixels`` to ``{image_filename}_pixels.json``."""
        if not self.image_filename:
            return
        json_filename = f"{self.image_filename}_pixels.json"
        with open(json_filename, "w") as f:
            json.dump({"pixels": [list(p) for p in self.pixels]}, f, indent=2)
        messagebox.showinfo(
            "Success", f"Pixel list saved successfully as {json_filename}"
        )

    def export_image(self) -> None:
        """Save an annotated copy of the image to ``{image_filename}_reference.png``."""
        if not self.image_filename or self.image is None:
            return
        image_filename = f"{self.image_filename}_reference.png"
        annotated_image = self.image.copy()
        draw = ImageDraw.Draw(annotated_image)
        font = ImageFont.load_default(size=16)
        for i, (x, y) in enumerate(self.pixels):
            draw.text((x, y), str(i + 1), fill="red", font=font)
        annotated_image.save(image_filename)
        messagebox.showinfo(
            "Success", f"Annotated image saved successfully as {image_filename}"
        )

    def quick_save(self) -> None:
        """Call ``save_json`` and ``export_image`` without a save dialog."""
        self.save_json()
        self.export_image()


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    _app = PixelSelectorApp(root, image_path)
    root.mainloop()
