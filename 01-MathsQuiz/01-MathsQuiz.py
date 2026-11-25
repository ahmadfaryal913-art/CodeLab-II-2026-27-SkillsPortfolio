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
    """Interactive Tkinter Maths Quiz application with Home, Difficulty, Quiz, and Results views."""

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

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Exercise 1 - Maths Quiz")
        self.root.geometry("660x480")
        self.root.minsize(600, 450)
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
        self.correct_first_try = 0
        self.correct_second_try = 0
        self.current_streak = 0
        self.best_streak = 0
        self.num1 = 0
        self.num2 = 0
        self.operator = "+"
        self.answer = 0
        self.quiz_active = False
        self._pending_after_id = None

        self.main_frame = tk.Frame(
            self.root,
            bg=self.BG_DARK,
            padx=20,
            pady=14,
            highlightbackground=self.ACCENT_GOLD,
            highlightthickness=1,
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.84)

        self.root.bind("<Configure>", self.on_window_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.displayHome()

    def set_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon-math_87982.ico")

        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass

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

    def on_window_resize(self, event):
        if event.widget is not self.root or self._bg_source_image is None:
            return

        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except ValueError:
                pass

        self._resize_after_id = self.root.after(80, self.render_background_image)

    def cancel_pending_timer(self):
        if self._pending_after_id is not None:
            try:
                self.root.after_cancel(self._pending_after_id)
            except ValueError:
                pass
            self._pending_after_id = None

    def clear_frame(self):
        self.cancel_pending_timer()
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def on_close(self):
        self.cancel_pending_timer()
        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except ValueError:
                pass
        self.root.destroy()

    # ------------------------------------------------------------------
    # Navigation & Screen Builders
    # ------------------------------------------------------------------

    def displayHome(self):
        """Render the application home page."""
        self.quiz_active = False
        self.clear_frame()

        header_frame = tk.Frame(self.main_frame, bg=self.BG_DARK)
        header_frame.pack(pady=(4, 4))

        tk.Label(
            header_frame,
            text="MATHS QUIZ STUDIO",
            font=(self.FONT_FAMILY, 20, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack()

        tk.Label(
            header_frame,
            text="Code Lab 2 • Interactive Arithmetic Assessment",
            font=(self.FONT_FAMILY, 9),
            bg=self.BG_DARK,
            fg=self.TEXT_MUTED,
        ).pack(pady=(2, 0))

        info_card = tk.Frame(
            self.main_frame,
            bg=self.PANEL_DARK,
            padx=16,
            pady=12,
            highlightbackground="#8bbbf6",
            highlightthickness=1,
        )
        info_card.pack(fill="x", pady=10)

        rules = [
            "• 10 questions per session with Addition (+) and Subtraction (-)",
            "• 1st attempt correct: +10 pts  |  2nd attempt correct: +5 pts",
            "• Switch back to Home anytime using the top navigation bar",
        ]
        for line in rules:
            tk.Label(
                info_card,
                text=line,
                font=(self.FONT_FAMILY, 9),
                bg=self.PANEL_DARK,
                fg=self.TEXT_LIGHT,
                anchor="w",
            ).pack(fill="x", pady=2)

        if self.best_score > 0:
            tk.Label(
                info_card,
                text=f"Session Best Score: {self.best_score} / {self.TOTAL_QUESTIONS * self.FIRST_ATTEMPT_POINTS}",
                font=(self.FONT_FAMILY, 9, "bold"),
                bg=self.PANEL_DARK,
                fg=self.ACCENT_GOLD,
                anchor="w",
            ).pack(fill="x", pady=(6, 0))

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
            width=18,
            pady=7,
            command=self.displayMenu,
        ).pack(pady=(4, 6))

        tk.Button(
            self.main_frame,
            text="Exit Application",
            font=(self.FONT_FAMILY, 9),
            bg=self.PANEL_DARK,
            fg=self.TEXT_MUTED,
            activebackground="#8bbbf6",
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=16,
            pady=4,
            command=self.on_close,
        ).pack()

    def displayMenu(self):
        """Render the difficulty selection screen with a Home button."""
        self.quiz_active = False
        self.clear_frame()

        nav_bar = tk.Frame(self.main_frame, bg=self.BG_DARK)
        nav_bar.pack(fill="x", pady=(0, 6))

        tk.Button(
            nav_bar,
            text="← Home",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.ACCENT_GOLD,
            activebackground="#8bbbf6",
            activeforeground=self.ACCENT_GOLD,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.displayHome,
        ).pack(side="left")

        tk.Label(
            self.main_frame,
            text="SELECT DIFFICULTY LEVEL",
            font=(self.FONT_FAMILY, 16, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(2, 3))

        tk.Label(
            self.main_frame,
            text="Choose a level to start your 10-question round:",
            font=(self.FONT_FAMILY, 9),
            bg=self.BG_DARK,
            fg=self.TEXT_MUTED,
        ).pack(pady=(0, 10))

        options = [
            ("1. Easy  •  Single Digit (1–9)", "Easy"),
            ("2. Moderate  •  Double Digit (10–99)", "Moderate"),
            ("3. Advanced  •  Four Digit (1000–9999)", "Advanced"),
        ]

        for label_text, level in options:
            tk.Button(
                self.main_frame,
                text=label_text,
                font=(self.FONT_FAMILY, 10, "bold"),
                bg=self.PANEL_DARK,
                fg=self.TEXT_LIGHT,
                activebackground=self.ACCENT_GOLD,
                activeforeground=self.TEXT_DARK,
                highlightbackground="#8bbbf6",
                highlightthickness=1,
                relief="flat",
                cursor="hand2",
                width=32,
                pady=7,
                command=lambda lvl=level: self.start_quiz(lvl),
            ).pack(pady=4)

    def confirm_return_home(self):
        """Allow returning to Home mid-quiz with confirmation so progress isn't lost accidentally."""
        if self.quiz_active:
            should_leave = messagebox.askyesno(
                "Return to Home",
                "A quiz is currently in progress. Return to the Home page?",
                parent=self.root,
            )
            if not should_leave:
                return
        self.displayHome()

    def build_quiz_screen(self):
        """Build the active quiz UI including a mid-session Home button."""
        self.clear_frame()

        top_bar = tk.Frame(self.main_frame, bg=self.BG_DARK)
        top_bar.pack(fill="x", pady=(0, 8))

        tk.Button(
            top_bar,
            text="← Home",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.ACCENT_GOLD,
            activebackground="#8bbbf6",
            activeforeground=self.ACCENT_GOLD,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.confirm_return_home,
        ).pack(side="left")

        self.q_label = tk.Label(
            top_bar,
            text=f"Question 1/{self.TOTAL_QUESTIONS} ({self.difficulty})",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.BG_DARK,
            fg=self.TEXT_LIGHT,
        )
        self.q_label.pack(side="left", padx=(10, 0))

        self.score_label = tk.Label(
            top_bar,
            text="Score: 0",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        )
        self.score_label.pack(side="right")

        problem_card = tk.Frame(
            self.main_frame,
            bg=self.CARD_LIGHT,
            padx=16,
            pady=12,
        )
        problem_card.pack(fill="x", pady=(0, 10))

        self.problem_label = tk.Label(
            problem_card,
            text="",
            font=(self.FONT_FAMILY, 20, "bold"),
            bg=self.CARD_LIGHT,
            fg=self.TEXT_DARK,
        )
        self.problem_label.pack()

        tk.Label(
            self.main_frame,
            text="Enter your answer:",
            font=(self.FONT_FAMILY, 9),
            bg=self.BG_DARK,
            fg=self.TEXT_MUTED,
        ).pack()

        self.answer_entry = tk.Entry(
            self.main_frame,
            font=(self.FONT_FAMILY, 12, "bold"),
            justify="center",
            width=14,
            bg=self.CARD_LIGHT,
            fg=self.TEXT_DARK,
            insertbackground=self.TEXT_DARK,
        )
        self.answer_entry.pack(pady=5)
        self.answer_entry.focus_set()
        self.answer_entry.bind("<Return>", lambda _event: self.check_input())

        self.submit_btn = tk.Button(
            self.main_frame,
            text="Submit Answer",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=16,
            pady=6,
            command=self.check_input,
        )
        self.submit_btn.pack(pady=5)

        self.feedback_label = tk.Label(
            self.main_frame,
            text="",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.BG_DARK,
            fg=self.TEXT_MUTED,
            wraplength=460,
        )
        self.feedback_label.pack(pady=(4, 0))

    # ------------------------------------------------------------------
    # Quiz Logic & Evaluation
    # ------------------------------------------------------------------

    def randomInt(self, level: str) -> int:
        if level == "Easy":
            return random.randint(1, 9)
        if level == "Moderate":
            return random.randint(10, 99)
        return random.randint(1000, 9999)

    def decideOperation(self) -> str:
        return random.choice(["+", "-"])

    def compute_expected_answer(self, num1: int, operator: str, num2: int) -> int:
        return num1 + num2 if operator == "+" else num1 - num2

    def start_quiz(self, difficulty: str):
        self.difficulty = difficulty
        self.question_num = 0
        self.attempt = 1
        self.score = 0
        self.correct_first_try = 0
        self.correct_second_try = 0
        self.current_streak = 0
        self.best_streak = 0
        self.quiz_active = True

        self.build_quiz_screen()
        self.next_question()

    def next_question(self):
        self._pending_after_id = None
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

    def displayProblem(self, num1: int, operator: str, num2: int):
        self.q_label.config(text=f"Question {self.question_num}/{self.TOTAL_QUESTIONS} ({self.difficulty})")
        self.score_label.config(text=f"Score: {self.score}")
        self.problem_label.config(text=f"{num1} {operator} {num2} =")
        self.feedback_label.config(text="", fg=self.TEXT_MUTED)
        self.answer_entry.config(state="normal")
        self.submit_btn.config(state="normal")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus_set()

    def check_input(self):
        if not self.quiz_active:
            return

        typed = self.answer_entry.get().strip()
        if not typed:
            self.feedback_label.config(text="Please enter an answer first.", fg=self.WARNING_COLOR)
            self.answer_entry.focus_set()
            return

        try:
            guess = int(typed)
        except ValueError:
            self.feedback_label.config(
                text="Invalid input. Please enter a whole number.",
                fg=self.ERROR_COLOR,
            )
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus_set()
            return

        self.isCorrect(guess)

    def _schedule_next(self, delay_ms: int):
        self.answer_entry.config(state="disabled")
        self.submit_btn.config(state="disabled")
        self._pending_after_id = self.root.after(delay_ms, self.next_question)

    def isCorrect(self, user_answer: int) -> bool:
        if user_answer == self.answer:
            points = self.FIRST_ATTEMPT_POINTS if self.attempt == 1 else self.SECOND_ATTEMPT_POINTS
            self.score += points
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)

            if self.attempt == 1:
                self.correct_first_try += 1
            else:
                self.correct_second_try += 1

            self.score_label.config(text=f"Score: {self.score}")
            self.feedback_label.config(
                text=f"Correct! +{points} points (Streak: {self.current_streak})",
                fg=self.SUCCESS_COLOR,
            )
            self._schedule_next(750)
            return True

        self.current_streak = 0
        if self.attempt == 1:
            self.attempt = 2
            self.feedback_label.config(
                text=f"Not quite. Try one more time for {self.SECOND_ATTEMPT_POINTS} points.",
                fg=self.WARNING_COLOR,
            )
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus_set()
            return False

        self.feedback_label.config(
            text=f"Incorrect. The correct answer was {self.answer}.",
            fg=self.ERROR_COLOR,
        )
        self._schedule_next(1000)
        return False

    # ------------------------------------------------------------------
    # Results & Grading
    # ------------------------------------------------------------------

    def calculate_grade(self, score: int) -> str:
        max_score = self.TOTAL_QUESTIONS * self.FIRST_ATTEMPT_POINTS
        percentage = (score / max_score) * 100
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

    def displayResults(self):
        """Display the final performance summary, grade, and navigation buttons."""
        self.quiz_active = False
        self.best_score = max(self.best_score, self.score)
        self.clear_frame()

        max_score = self.TOTAL_QUESTIONS * self.FIRST_ATTEMPT_POINTS
        grade = self.calculate_grade(self.score)
        total_solved = self.correct_first_try + self.correct_second_try

        tk.Label(
            self.main_frame,
            text="QUIZ COMPLETED",
            font=(self.FONT_FAMILY, 18, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(2, 4))

        summary_card = tk.Frame(
            self.main_frame,
            bg=self.PANEL_DARK,
            padx=16,
            pady=12,
            highlightbackground="#8bbbf6",
            highlightthickness=1,
        )
        summary_card.pack(fill="x", pady=6)

        tk.Label(
            summary_card,
            text=f"Final Score: {self.score} / {max_score}   •   Grade: {grade}",
            font=(self.FONT_FAMILY, 13, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).pack(pady=(0, 6))

        tk.Label(
            summary_card,
            text=(
                f"Solved: {total_solved}/{self.TOTAL_QUESTIONS}  "
                f"(1st Try: {self.correct_first_try}, 2nd Try: {self.correct_second_try})  •  "
                f"Best Streak: {self.best_streak}"
            ),
            font=(self.FONT_FAMILY, 9),
            bg=self.PANEL_DARK,
            fg=self.TEXT_MUTED,
            wraplength=450,
        ).pack()

        btn_row = tk.Frame(self.main_frame, bg=self.BG_DARK)
        btn_row.pack(pady=10)

        tk.Button(
            btn_row,
            text="Play Again",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=14,
            pady=6,
            command=self.displayMenu,
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            btn_row,
            text="← Home",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
            activebackground="#8bbbf6",
            activeforeground=self.ACCENT_GOLD,
            relief="flat",
            cursor="hand2",
            width=13,
            pady=6,
            command=self.displayHome,
        ).grid(row=0, column=1, padx=6)

        self.main_frame.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = MathsQuizApp(root)
    root.mainloop()