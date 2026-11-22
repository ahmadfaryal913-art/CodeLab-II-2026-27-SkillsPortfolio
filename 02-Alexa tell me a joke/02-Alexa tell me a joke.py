import os
import random
import tkinter as tk


class JokeAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise 2 - Alexa Tell Me a Joke")
        self.root.geometry("520x370")
        self.root.resizable(0, 0)
        self.root.configure(bg="#182032")

        self.set_icon()

        self.jokes = []
        self.current_joke = None
        self.last_index = -1

        self.load_jokes()

        self.main_frame = tk.Frame(self.root, bg="#182032")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.build_ui()

    def set_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "laughing_109972.ico")

        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass

    def load_jokes(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, "randomJokes.txt"),
            os.path.join(base_dir, "resources", "randomJokes.txt"),
            os.path.join(base_dir, "..", "resources", "randomJokes.txt"),
        ]

        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            self.jokes = [
                ("Why did the chicken cross the road?", "To get to the other side.")
            ]
            return

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                if "?" in line:
                    setup_part, punchline_part = line.split("?", 1)
                    setup = setup_part.strip() + "?"
                    punchline = punchline_part.strip()
                    if not punchline:
                        punchline = "No punchline found."
                else:
                    setup = line
                    punchline = ""

                self.jokes.append((setup, punchline))

        if not self.jokes:
            self.jokes = [
                ("Why did the chicken cross the road?", "To get to the other side.")
            ]

    def build_ui(self):
        tk.Label(
            self.main_frame,
            text="Alexa Tell Me a Joke",
            font=("Tahoma", 18, "bold"),
            bg="#AABEED",
            fg="#ffd166",
        ).pack(pady=(4, 12))

        self.alexa_btn = tk.Button(
            self.main_frame,
            text="Alexa tell me a Joke",
            font=("Tahoma", 11, "bold"),
            bg="#e6a817",
            fg="#000000",
            activebackground="#cf940e",
            activeforeground="#000000",
            width=22,
            pady=6,
            command=self.tell_joke,
        )
        self.alexa_btn.pack(pady=5)

        joke_box = tk.Frame(
            self.main_frame,
            bg="#fffdf7",
            bd=2,
            relief="solid",
            padx=16,
            pady=14,
        )
        joke_box.pack(fill="x", pady=12)

        self.setup_label = tk.Label(
            joke_box,
            text="Click 'Alexa tell me a Joke' to hear something funny!",
            font=("Tahoma", 11, "bold"),
            bg="#fffdf7",
            fg="#AABEED",
            wraplength=430,
            justify="center",
        )
        self.setup_label.pack(pady=(0, 8))

        self.punchline_label = tk.Label(
            joke_box,
            text="",
            font=("Tahoma", 11, "bold"),
            bg="#fffdf7",
            fg="#1b7f69",
            wraplength=430,
            justify="center",
        )
        self.punchline_label.pack()

        btn_row = tk.Frame(self.main_frame, bg="#182032")
        btn_row.pack(pady=8)

        self.punchline_btn = tk.Button(
            btn_row,
            text="Show Punchline",
            font=("Tahoma", 10, "bold"),
            bg="#AABEED",
            fg="#ffffff",
            activebackground="#AABEED",
            activeforeground="#ffffff",
            width=15,
            pady=5,
            state="disabled",
            command=self.show_punchline,
        )
        self.punchline_btn.grid(row=0, column=0, padx=6)

        self.next_btn = tk.Button(
            btn_row,
            text="Next Joke",
            font=("Tahoma", 10, "bold"),
            bg="#e6a817",
            fg="#000000",
            activebackground="#cf940e",
            activeforeground="#000000",
            width=15,
            pady=5,
            command=self.tell_joke,
        )
        self.next_btn.grid(row=0, column=1, padx=6)

        tk.Button(
            self.main_frame,
            text="Quit",
            font=("Tahoma", 10, "bold"),
            bg="#d94e3f",
            fg="#ffffff",
            activebackground="#b83d30",
            activeforeground="#ffffff",
            width=14,
            pady=5,
            command=self.root.destroy,
        ).pack(pady=(10, 0))

    def tell_joke(self):
        if len(self.jokes) > 1:
            index = random.randint(0, len(self.jokes) - 1)
            while index == self.last_index:
                index = random.randint(0, len(self.jokes) - 1)
            self.last_index = index
        else:
            index = 0

        self.current_joke = self.jokes[index]
        setup, _ = self.current_joke

        self.setup_label.config(text=setup)
        self.punchline_label.config(text="")
        self.punchline_btn.config(state="normal")

    def show_punchline(self):
        if self.current_joke is not None:
            _, punchline = self.current_joke
            self.punchline_label.config(text=punchline)


if __name__ == "__main__":
    root = tk.Tk()
    app = JokeAssistantApp(root)
    root.mainloop()