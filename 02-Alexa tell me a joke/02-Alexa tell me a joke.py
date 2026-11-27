import os
import random
import tkinter as tk

try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class JokeAssistantApp:
    """Interactive Tkinter joke assistant with Home screen, joke viewer, and Pillow background."""

    BG_IMAGE_FILENAME = "exercise 2 background.webp"
    ICON_FILENAME = "laughing_109972.ico"

    # Consistent portfolio theme palette
    BG_DARK = "#162232"
    PANEL_DARK = "#1e2e42"
    CARD_LIGHT = "#f4f6f9"
    ACCENT_GOLD = "#f7be44"
    ACCENT_GOLD_HOVER = "#e5ac2e"
    TEXT_LIGHT = "#ffffff"
    TEXT_MUTED = "#b8c7d9"
    TEXT_DARK = "#162232"
    PUNCHLINE_COLOR = "#1b7f69"
    DANGER_BG = "#c0392b"
    DANGER_HOVER = "#9e2d21"

    FONT_FAMILY = "Tahoma"

    # Initialize the window, icon, background image, joke list, and Home screen
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Exercise 2 - Alexa Tell Me a Joke")
        self.root.geometry("680x480")
        self.root.minsize(580, 440)
        self.root.configure(bg=self.BG_DARK)

        self.set_icon()

        # Background image state
        self._bg_source_image = None
        self._bg_photo_image = None
        self._resize_after_id = None
        self.bg_label = tk.Label(self.root, bg=self.BG_DARK)
        self.bg_label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.load_background_image()

        # Joke state
        self.jokes = []
        self.current_joke = None
        self.last_index = -1
        self.jokes_told_count = 0
        self.info_visible = False
        self.load_jokes()

        # Compact centered card so there is minimal empty space below the buttons
        self.main_frame = tk.Frame(
            self.root,
            bg=self.BG_DARK,
            padx=18,
            pady=14,
            highlightbackground=self.ACCENT_GOLD,
            highlightthickness=2,
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.50, relheight=0.40)

        self.root.bind("<Configure>", self.on_window_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.displayHome()

    # Adjust card height when the info box is toggled so it fits neatly
    def _sync_card_size(self):
        if self.info_visible:
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.54, relheight=0.54)
        else:
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.50, relheight=0.40)

    # Set custom application window icon if available
    def set_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, self.ICON_FILENAME)

        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass

    # Load background image using Pillow so it can be scaled dynamically
    def load_background_image(self):
        if not PIL_AVAILABLE:
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, self.BG_IMAGE_FILENAME)

        if os.path.exists(bg_path):
            try:
                self._bg_source_image = Image.open(bg_path).convert("RGB")
                self.render_background_image()
            except Exception:
                self._bg_source_image = None

    # Resize and render the background image to match the window size
    def render_background_image(self):
        self._resize_after_id = None
        if not PIL_AVAILABLE or self._bg_source_image is None:
            return

        width = max(self.root.winfo_width(), 1)
        height = max(self.root.winfo_height(), 1)

        try:
            resampling = Image.Resampling.LANCZOS
        except AttributeError:
            resampling = Image.LANCZOS

        resized = self._bg_source_image.resize((width, height), resampling)
        self._bg_photo_image = ImageTk.PhotoImage(resized)
        self.bg_label.config(image=self._bg_photo_image)
        self.bg_label.lower()

    # Debounce window resize events for smooth background redrawing
    def on_window_resize(self, event):
        if event.widget is not self.root or self._bg_source_image is None:
            return

        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except ValueError:
                pass

        self._resize_after_id = self.root.after(80, self.render_background_image)

    # Clear all child widgets inside main_frame before switching views
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Cancel any pending resize timer and close the application window
    def on_close(self):
        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except ValueError:
                pass
        self.root.destroy()

    # Locate randomJokes.txt across expected project paths
    def _find_jokes_file(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, "randomJokes.txt"),
            os.path.join(base_dir, "resources", "randomJokes.txt"),
            os.path.join(base_dir, "..", "resources", "randomJokes.txt"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    # Parse a single joke line into a (setup, punchline) tuple
    def _parse_joke_line(self, line: str):
        cleaned = line.strip()
        if not cleaned:
            return None

        if "?" in cleaned:
            setup_part, punchline_part = cleaned.split("?", 1)
            setup = setup_part.strip() + "?"
            punchline = punchline_part.strip() or "No punchline found."
            return (setup, punchline)

        return (cleaned, "No punchline found.")

    # Load all jokes from file with fallback handling if missing or empty
    def load_jokes(self):
        file_path = self._find_jokes_file()
        parsed_jokes = []

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        item = self._parse_joke_line(line)
                        if item is not None:
                            parsed_jokes.append(item)
            except OSError:
                parsed_jokes = []

        if not parsed_jokes:
            parsed_jokes = [
                ("Why did the chicken cross the road?", "To get to the other side.")
            ]

        self.jokes = parsed_jokes

    # Pick a random joke without repeating the immediately previous joke
    def _pick_next_joke(self):
        if len(self.jokes) > 1:
            index = random.randint(0, len(self.jokes) - 1)
            while index == self.last_index:
                index = random.randint(0, len(self.jokes) - 1)
            self.last_index = index
        else:
            index = 0

        self.current_joke = self.jokes[index]
        self.jokes_told_count += 1
        return self.current_joke

    # Toggle visibility of the extra info box on the Home screen
    def toggle_info(self):
        self.info_visible = not self.info_visible
        self.displayHome()

    # Render the Home screen with larger buttons and a compact card layout
    def displayHome(self):
        self.info_visible = False
        self._sync_card_size()
        self.clear_frame()

        tk.Label(
            self.main_frame,
            text="ALEXA JOKE ASSISTANT",
            font=(self.FONT_FAMILY, 19, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(2, 10))

        tk.Button(
            self.main_frame,
            text="Open Joke Assistant →",
            font=(self.FONT_FAMILY, 12, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=26,
            pady=10,
            command=self.build_ui,
        ).pack(pady=6)

        tk.Button(
            self.main_frame,
            text="How It Works",
            font=(self.FONT_FAMILY, 11, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            activebackground="#273b54",
            activeforeground=self.ACCENT_GOLD,
            relief="flat",
            cursor="hand2",
            width=26,
            pady=9,
            command=self._show_info_view,
        ).pack(pady=6)

        tk.Button(
            self.main_frame,
            text="Quit",
            font=(self.FONT_FAMILY, 11, "bold"),
            bg=self.DANGER_BG,
            fg=self.TEXT_LIGHT,
            activebackground=self.DANGER_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=24,
            pady=9,
            command=self.on_close,
        ).pack(pady=(6, 2))

    # Expand the card slightly when showing the How It Works details
    def _show_info_view(self):
        self.info_visible = True
        self._sync_card_size()
        self.clear_frame()

        tk.Label(
            self.main_frame,
            text="HOW IT WORKS",
            font=(self.FONT_FAMILY, 17, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(2, 8))

        info_card = tk.Frame(
            self.main_frame,
            bg=self.PANEL_DARK,
            padx=14,
            pady=10,
            highlightbackground=self.ACCENT_GOLD,
            highlightthickness=1,
        )
        info_card.pack(fill="x", pady=4)

        tk.Label(
            info_card,
            text=f"Jokes Loaded: {len(self.jokes)}  |  Viewed: {self.jokes_told_count}",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.PANEL_DARK,
            fg=self.ACCENT_GOLD,
        ).pack()

        tk.Label(
            info_card,
            text="Click 'Alexa tell me a Joke' for the setup, then click 'Show Punchline'.",
            font=(self.FONT_FAMILY, 10),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            wraplength=360,
        ).pack(pady=(4, 0))

        tk.Button(
            self.main_frame,
            text="← Back",
            font=(self.FONT_FAMILY, 11, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=20,
            pady=8,
            command=self.displayHome,
        ).pack(pady=(10, 2))

    # Render the main joke viewer screen with Home navigation and larger buttons
    def build_ui(self):
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.60, relheight=0.54)
        self.clear_frame()

        top_bar = tk.Frame(self.main_frame, bg=self.BG_DARK)
        top_bar.pack(fill="x", pady=(0, 6))

        tk.Button(
            top_bar,
            text="← Home",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.PANEL_DARK,
            fg=self.ACCENT_GOLD,
            activebackground="#273b54",
            activeforeground=self.ACCENT_GOLD,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.displayHome,
        ).pack(side="left")

        self.counter_label = tk.Label(
            top_bar,
            text=f"Jokes Told: {self.jokes_told_count}",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.BG_DARK,
            fg=self.TEXT_MUTED,
        )
        self.counter_label.pack(side="right")

        tk.Label(
            self.main_frame,
            text="Alexa Tell Me a Joke",
            font=(self.FONT_FAMILY, 17, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(0, 6))

        self.alexa_btn = tk.Button(
            self.main_frame,
            text="Alexa tell me a Joke",
            font=(self.FONT_FAMILY, 11, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=26,
            pady=9,
            command=self.tell_joke,
        )
        self.alexa_btn.pack(pady=4)

        joke_box = tk.Frame(
            self.main_frame,
            bg=self.CARD_LIGHT,
            bd=1,
            relief="solid",
            padx=14,
            pady=10,
        )
        joke_box.pack(fill="x", pady=8)

        initial_setup = (
            self.current_joke[0]
            if self.current_joke is not None
            else "Click 'Alexa tell me a Joke' to hear something funny!"
        )

        self.setup_label = tk.Label(
            joke_box,
            text=initial_setup,
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.CARD_LIGHT,
            fg=self.TEXT_DARK,
            wraplength=380,
            justify="center",
        )
        self.setup_label.pack(pady=(0, 6))

        self.punchline_label = tk.Label(
            joke_box,
            text="",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.CARD_LIGHT,
            fg=self.PUNCHLINE_COLOR,
            wraplength=380,
            justify="center",
        )
        self.punchline_label.pack()

        btn_row = tk.Frame(self.main_frame, bg=self.BG_DARK)
        btn_row.pack(pady=6)

        self.punchline_btn = tk.Button(
            btn_row,
            text="Show Punchline",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            activebackground="#273b54",
            activeforeground=self.ACCENT_GOLD,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=8,
            state="normal" if self.current_joke is not None else "disabled",
            command=self.show_punchline,
        )
        self.punchline_btn.grid(row=0, column=0, padx=6)

        self.next_btn = tk.Button(
            btn_row,
            text="Next Joke",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=8,
            command=self.tell_joke,
        )
        self.next_btn.grid(row=0, column=1, padx=6)

        tk.Button(
            self.main_frame,
            text="Quit",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.DANGER_BG,
            fg=self.TEXT_LIGHT,
            activebackground=self.DANGER_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=8,
            command=self.on_close,
        ).pack(pady=(6, 0))

    # Display the next joke setup, reset the punchline, and enable the punchline button
    def tell_joke(self):
        setup, _ = self._pick_next_joke()
        self.setup_label.config(text=setup)
        self.punchline_label.config(text="")
        self.punchline_btn.config(state="normal")
        self.counter_label.config(text=f"Jokes Told: {self.jokes_told_count}")

    # Reveal the punchline for the currently displayed joke
    def show_punchline(self):
        if self.current_joke is not None:
            _, punchline = self.current_joke
            self.punchline_label.config(text=punchline)


if __name__ == "__main__":
    root = tk.Tk()
    app = JokeAssistantApp(root)
    root.mainloop()