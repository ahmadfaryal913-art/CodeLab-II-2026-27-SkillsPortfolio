import os
import random
import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class MathsQuizApp:
    """Interactive Tkinter Maths Quiz application following brief functions and High First standards."""

    TOTAL_QUESTIONS = 10
    FIRST_ATTEMPT_POINTS = 10
    SECOND_ATTEMPT_POINTS = 5
    BG_IMAGE_FILENAME = "exercise 1 background.jpg"

    # Consistent portfolio theme palette
    BG_DARK = "#8bbbf6"
    PANEL_DARK = "#244670"
    CARD_LIGHT = "#050506"
    ACCENT_GOLD = "#07070a"
    ACCENT_GOLD_HOVER = "#e5ac2e"
    TEXT_LIGHT = "#FFFFFF"
    TEXT_MUTED = "#FFFFFF"
    TEXT_DARK = "#FFFFFF"
    SUCCESS_COLOR = "#000000"
    WARNING_COLOR = "#0e0d0b"
    ERROR_COLOR = "#ff6b6b"

    FONT_FAMILY = "Tahoma"

    # Initialize the window, background image, quiz state, and compact Home card
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Exercise 1 - Maths Quiz")
        self.root.geometry("760x540")
        self.root.minsize(640, 480)
        self.root.configure(bg=self.BG_DARK)

        self.set_icon()

        # Background image state
        self._bg_source_image = None
        self._bg_photo_image = None
        self._resize_after_id = None
        self.bg_label = tk.Label(self.root, bg=self.BG_DARK)
        self.bg_label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.load_background_image()

        # Quiz state variables
        self.difficulty = "Easy"
        self.question_num = 0
        self.attempt = 1
        self.score = 0
        self.best_score = 0
        self.current_streak = 0
        self.best_streak = 0
        self.num1 = 0
        self.num2 = 0
        self.operator = "+"
        self.answer = 0
        self.quiz_active = False
        self.rules_visible = False

        # Compact centered card so there is less empty blue space
        self.main_frame = tk.Frame(
            self.root,
            bg=self.BG_DARK,
            padx=14,
            pady=10,
            highlightbackground=self.ACCENT_GOLD,
            highlightthickness=2,
        )
        self._sync_card_size()

        self.root.bind("<Configure>", self.on_window_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.displayHome()

    # Adjust card size slightly when rules are expanded or during quiz/results views
    def _sync_card_size(self, expanded: bool = False):
        if expanded:
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.44, relheight=0.52)
        else:
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.40, relheight=0.40)

    # Set custom application window icon if present in the script folder
    def set_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon-math_87982.ico")

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

    # Resize background image to match current window dimensions
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

    # Debounce window resize events to keep resizing smooth
    def on_window_resize(self, event):
        if event.widget is not self.root or self._bg_source_image is None:
            return

        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except ValueError:
                pass

        self._resize_after_id = self.root.after(80, self.render_background_image)

    # Clear all widgets inside main_frame before building a new view
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Clean up pending resize callback and close the application window
    def on_close(self):
        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except ValueError:
                pass
        self.root.destroy()

    # Toggle visibility of quiz rules when the user clicks the Rules button
    def toggle_rules(self):
        self.rules_visible = not self.rules_visible
        self.displayHome()

    # Display the Home screen with Start Quiz, Rules button, and Exit button
    def displayHome(self):
        self.quiz_active = False
        self._sync_card_size(expanded=self.rules_visible)
        self.clear_frame()

        tk.Label(
            self.main_frame,
            text="MATHS QUIZ",
            font=(self.FONT_FAMILY, 19, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(2, 6))

        if self.best_score > 0:
            tk.Label(
                self.main_frame,
                text=f"Best Score: {self.best_score} / {self.TOTAL_QUESTIONS * self.FIRST_ATTEMPT_POINTS}",
                font=(self.FONT_FAMILY, 9, "bold"),
                bg=self.BG_DARK,
                fg=self.TEXT_LIGHT,
            ).pack(pady=(0, 4))

        tk.Button(
            self.main_frame,
            text="Start Quiz →",
            font=(self.FONT_FAMILY, 11, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=20,
            pady=7,
            command=self.displayMenu,
        ).pack(pady=3)

        tk.Button(
            self.main_frame,
            text="Quiz Rules",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            activebackground="#1b3554",
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=20,
            pady=6,
            command=self.toggle_rules,
        ).pack(pady=3)

        if self.rules_visible:
            rules_box = tk.Frame(
                self.main_frame,
                bg=self.PANEL_DARK,
                padx=10,
                pady=6,
                highlightbackground=self.ACCENT_GOLD,
                highlightthickness=1,
            )
            rules_box.pack(fill="x", pady=4)
            tk.Label(
                rules_box,
                text="10 questions (+ / -)\n1st try: +10 pts | 2nd try: +5 pts",
                font=(self.FONT_FAMILY, 9, "bold"),
                bg=self.PANEL_DARK,
                fg=self.TEXT_LIGHT,
            ).pack()

        tk.Button(
            self.main_frame,
            text="Exit",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_MUTED,
            activebackground="#1b3554",
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=6,
            command=self.on_close,
        ).pack(pady=(4, 2))

    # Display the difficulty selection menu at the start of a quiz round
    def displayMenu(self):
        self.quiz_active = False
        self._sync_card_size(expanded=True)
        self.clear_frame()

        nav_bar = tk.Frame(self.main_frame, bg=self.BG_DARK)
        nav_bar.pack(fill="x", pady=(0, 4))

        tk.Button(
            nav_bar,
            text="← Home",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            activebackground="#1b3554",
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.displayHome,
        ).pack(side="left")

        tk.Label(
            self.main_frame,
            text="DIFFICULTY LEVEL",
            font=(self.FONT_FAMILY, 16, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(2, 8))

        levels = [
            ("Easy (1–9)", "Easy"),
            ("Moderate (10–99)", "Moderate"),
            ("Advanced (1000–9999)", "Advanced"),
        ]

        for button_text, level_name in levels:
            tk.Button(
                self.main_frame,
                text=button_text,
                font=(self.FONT_FAMILY, 10, "bold"),
                bg=self.PANEL_DARK,
                fg=self.TEXT_LIGHT,
                activebackground=self.ACCENT_GOLD,
                activeforeground=self.TEXT_DARK,
                relief="flat",
                cursor="hand2",
                width=22,
                pady=7,
                command=lambda lvl=level_name: self.start_quiz(lvl),
            ).pack(pady=4)

    # Confirm before returning to Home mid-quiz so current progress isn't lost by mistake
    def confirm_return_home(self):
        if self.quiz_active:
            leave = messagebox.askyesno(
                "Return to Home",
                "Leave the current quiz and return to Home?",
                parent=self.root,
            )
            if not leave:
                return
        self.displayHome()

    # Determine min and max random integer bounds based on chosen difficulty
    def randomInt(self, level: str) -> int:
        if level == "Easy":
            return random.randint(1, 9)
        if level == "Moderate":
            return random.randint(10, 99)
        return random.randint(1000, 9999)

    # Randomly decide whether the arithmetic operation is '+' or '-'
    def decideOperation(self) -> str:
        return random.choice(["+", "-"])

    # Compute the expected answer for the generated arithmetic expression
    def compute_expected_answer(self, num1: int, operator: str, num2: int) -> int:
        return num1 + num2 if operator == "+" else num1 - num2

    # Start a fresh 10-question session for the selected difficulty
    def start_quiz(self, difficulty: str):
        self.difficulty = difficulty
        self.question_num = 0
        self.attempt = 1
        self.score = 0
        self.current_streak = 0
        self.best_streak = 0
        self.quiz_active = True
        self.next_question()

    # Advance to the next question or display final results after 10 questions
    def next_question(self):
        if not self.quiz_active:
            return

        if self.question_num >= self.TOTAL_QUESTIONS:
            self.displayResults()
            return

        self.question_num += 1
        self.attempt = 1
        self.num1 = self.randomInt(self.difficulty)
        self.num2 = self.randomInt(self.difficulty)
        self.operator = self.decideOperation()
        self.answer = self.compute_expected_answer(self.num1, self.operator, self.num2)

        self.displayProblem(self.num1, self.operator, self.num2)

    # Display the current math problem, Entry box, and Submit button
    def displayProblem(self, num1: int, operator: str, num2: int):
        self._sync_card_size(expanded=True)
        self.clear_frame()

        top_bar = tk.Frame(self.main_frame, bg=self.BG_DARK)
        top_bar.pack(fill="x", pady=(0, 6))

        tk.Button(
            top_bar,
            text="← Home",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            activebackground="#1b3554",
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=9,
            pady=3,
            command=self.confirm_return_home,
        ).pack(side="left")

        tk.Label(
            top_bar,
            text=f"Q {self.question_num}/{self.TOTAL_QUESTIONS}",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.BG_DARK,
            fg=self.TEXT_LIGHT,
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            top_bar,
            text=f"Score: {self.score}",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(side="right")

        problem_card = tk.Frame(
            self.main_frame,
            bg=self.CARD_LIGHT,
            padx=12,
            pady=10,
        )
        problem_card.pack(fill="x", pady=(2, 8))

        tk.Label(
            problem_card,
            text=f"{num1} {operator} {num2} =",
            font=(self.FONT_FAMILY, 19, "bold"),
            bg=self.CARD_LIGHT,
            fg=self.TEXT_DARK,
        ).pack()

        self.answer_entry = tk.Entry(
            self.main_frame,
            font=(self.FONT_FAMILY, 11, "bold"),
            justify="center",
            width=14,
            bg=self.CARD_LIGHT,
            fg=self.TEXT_DARK,
            insertbackground=self.TEXT_DARK,
        )
        self.answer_entry.pack(pady=4)
        self.answer_entry.focus_set()
        self.answer_entry.bind("<Return>", lambda _event: self.check_input())

        tk.Button(
            self.main_frame,
            text="Submit Answer",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=7,
            command=self.check_input,
        ).pack(pady=6)

    # Validate user input and pass the integer answer to isCorrect
    def check_input(self):
        if not self.quiz_active:
            return

        raw_value = self.answer_entry.get().strip()
        if not raw_value:
            messagebox.showwarning("Input Required", "Please enter an answer first.", parent=self.root)
            self.answer_entry.focus_set()
            return

        try:
            user_guess = int(raw_value)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid whole number.", parent=self.root)
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus_set()
            return

        self.isCorrect(user_guess)

    # Check whether the user's answer is right and show pop-up feedback for each attempt
    def isCorrect(self, user_answer: int) -> bool:
        if user_answer == self.answer:
            points_earned = (
                self.FIRST_ATTEMPT_POINTS if self.attempt == 1 else self.SECOND_ATTEMPT_POINTS
            )
            self.score += points_earned
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)

            messagebox.showinfo(
                "Correct!",
                f"Correct! You earned {points_earned} points.",
                parent=self.root,
            )
            self.next_question()
            return True

        self.current_streak = 0

        # First wrong attempt: pop-up tells user they can try again for 5 points
        if self.attempt == 1:
            self.attempt = 2
            messagebox.showwarning(
                "Try Again",
                f"Not quite! Try one more time — you can earn {self.SECOND_ATTEMPT_POINTS} points on your second attempt.",
                parent=self.root,
            )
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus_set()
            return False

        # Second wrong attempt: show correct answer in pop-up and move to next question
        messagebox.showinfo(
            "Incorrect",
            f"Incorrect. The correct answer was {self.answer}.",
            parent=self.root,
        )
        self.next_question()
        return False

    # Calculate final grade from the percentage of total possible points
    def calculate_grade(self, final_score: int) -> str:
        max_score = self.TOTAL_QUESTIONS * self.FIRST_ATTEMPT_POINTS
        percentage = (final_score / max_score) * 100
        if percentage >= 90:
            return "A+"
        if percentage >= 80:
            return "A"
        if percentage >= 70:
            return "B"
        if percentage >= 60:
            return "C"
        if percentage >= 50:
            return "D"
        return "F"

    # Display final score, grade, best streak, and Play Again / Home buttons
    def displayResults(self):
        self.quiz_active = False
        self._sync_card_size(expanded=True)
        self.best_score = max(self.best_score, self.score)
        self.clear_frame()

        max_score = self.TOTAL_QUESTIONS * self.FIRST_ATTEMPT_POINTS
        grade = self.calculate_grade(self.score)

        tk.Label(
            self.main_frame,
            text="QUIZ RESULTS",
            font=(self.FONT_FAMILY, 17, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(2, 6))

        result_box = tk.Frame(
            self.main_frame,
            bg=self.PANEL_DARK,
            padx=12,
            pady=10,
            highlightbackground=self.ACCENT_GOLD,
            highlightthickness=1,
        )
        result_box.pack(fill="x", pady=4)

        tk.Label(
            result_box,
            text=f"Score: {self.score} / {max_score}  •  Grade: {grade}",
            font=(self.FONT_FAMILY, 11, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).pack(pady=(0, 3))

        tk.Label(
            result_box,
            text=f"Best Streak: {self.best_streak}",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_MUTED,
        ).pack()

        tk.Button(
            self.main_frame,
            text="Play Again",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=7,
            command=self.displayMenu,
        ).pack(pady=(8, 4))

        tk.Button(
            self.main_frame,
            text="← Home",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            activebackground="#1b3554",
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=6,
            command=self.displayHome,
        ).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = MathsQuizApp(root)
    root.mainloop()