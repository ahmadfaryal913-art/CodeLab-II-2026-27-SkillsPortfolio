import os
import random
import tkinter as tk
from tkinter import messagebox


class MathsQuizApp:
    TOTAL_QUESTIONS = 10

    def __init__(self, root):
        self.root = root
        self.root.title("Exercise 1 - Maths Quiz")
        self.root.geometry("500x370")
        self.root.configure(bg="#aac4e1")

        self.set_icon()

        self.difficulty = "Easy"
        self.question_num = 0
        self.attempt = 1
        self.score = 0
        self.num1 = 0
        self.num2 = 0
        self.operator = "+"
        self.answer = 0

        self.main_frame = tk.Frame(self.root, bg="#b3c9e2", padx=24, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        self.displayMenu()

    def set_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon-math_87982.ico")

        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass
        else:
            print("Icon not found at:", icon_path)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def displayMenu(self):
        self.clear_frame()

        tk.Label(
            self.main_frame,
            text="DIFFICULTY LEVEL",
            font=("Arial", 18, "bold"),
            bg="#a4bedb",
            fg="#2b5b84",
        ).pack(pady=(8, 6))

        tk.Label(
            self.main_frame,
            text="Choose a level to start (10 questions):",
            font=("Arial", 10),
            bg="#a2b9d3",
            fg="#52657a",
        ).pack(pady=(0, 16))

        options = [
            ("1. Easy (Single digit)", "Easy"),
            ("2. Moderate (Double digit)", "Moderate"),
            ("3. Advanced (4-digit)", "Advanced"),
        ]

        for label_text, level in options:
            tk.Button(
                self.main_frame,
                text=label_text,
                font=("Arial", 11, "bold"),
                bg="#2b5b84",
                fg="white",
                activebackground="#1f4463",
                activeforeground="white",
                width=28,
                pady=7,
                command=lambda lvl=level: self.start_quiz(lvl),
            ).pack(pady=6)

    def start_quiz(self, difficulty):
        self.difficulty = difficulty
        self.question_num = 0
        self.score = 0
        self.build_quiz_screen()
        self.next_question()

    def build_quiz_screen(self):
        self.clear_frame()

        top_row = tk.Frame(self.main_frame, bg="#8f9fb1")
        top_row.pack(fill="x", pady=(0, 12))

        self.q_label = tk.Label(
            top_row,
            text=f"Question 1/{self.TOTAL_QUESTIONS}",
            font=("Arial", 10, "bold"),
            bg="#97ADC6",
            fg="#172536",
        )
        self.q_label.pack(side="left")

        self.score_label = tk.Label(
            top_row,
            text="Score: 0",
            font=("Arial", 10, "bold"),
            bg="#adc1d5",
            fg="#2b5b84",
        )
        self.score_label.pack(side="right")

        box = tk.Frame(
            self.main_frame,
            bg="#f9f6f6",
            bd=1,
            relief="solid",
            padx=20,
            pady=14,
        )
        box.pack(fill="x", pady=(0, 12))

        self.problem_label = tk.Label(
            box,
            text="",
            font=("Arial", 22, "bold"),
            bg="#ffffff",
            fg="#172536",
        )
        self.problem_label.pack()

        tk.Label(
            self.main_frame,
            text="Enter your answer:",
            font=("Arial", 10),
            bg="#9db2c9",
            fg="#172536",
        ).pack()

        self.answer_entry = tk.Entry(
            self.main_frame,
            font=("Arial", 13),
            justify="center",
            width=14,
            bg="#ffffff",
            fg="#172536",
        )
        self.answer_entry.pack(pady=8)
        self.answer_entry.focus()
        self.answer_entry.bind("<Return>", lambda event: self.check_input())

        tk.Button(
            self.main_frame,
            text="Submit Answer",
            font=("Arial", 11, "bold"),
            bg="#2e7d5b",
            fg="white",
            activebackground="#225e44",
            activeforeground="white",
            width=18,
            pady=6,
            command=self.check_input,
        ).pack(pady=6)

        self.feedback_label = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 10, "bold"),
            bg="#b3c8e0",
            fg="#52657a",
            wraplength=420,
        )
        self.feedback_label.pack(pady=(8, 0))

    def randomInt(self, level):
        if level == "Easy":
            return random.randint(1, 9)
        elif level == "Moderate":
            return random.randint(10, 99)
        else:
            return random.randint(1000, 9999)

    def decideOperation(self):
        return random.choice(["+", "-"])

    def next_question(self):
        if self.question_num >= self.TOTAL_QUESTIONS:
            self.displayResults()
            return

        self.question_num += 1
        self.attempt = 1
        self.num1 = self.randomInt(self.difficulty)
        self.num2 = self.randomInt(self.difficulty)
        self.operator = self.decideOperation()

        if self.operator == "+":
            self.answer = self.num1 + self.num2
        else:
            self.answer = self.num1 - self.num2

        self.displayProblem(self.num1, self.operator, self.num2)

    def displayProblem(self, num1, operator, num2):
        self.q_label.config(text=f"Question {self.question_num}/{self.TOTAL_QUESTIONS}")
        self.score_label.config(text=f"Score: {self.score}")
        self.problem_label.config(text=f"{num1} {operator} {num2} =")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()

    def check_input(self):
        typed = self.answer_entry.get().strip()
        if not typed:
            self.feedback_label.config(text="Please type an answer first.", fg="#b76e00")
            return

        try:
            guess = int(typed)
        except ValueError:
            self.feedback_label.config(text="Please enter a valid number.", fg="#c0392b")
            return

        self.isCorrect(guess)

    def isCorrect(self, user_answer):
        if user_answer == self.answer:
            points = 10 if self.attempt == 1 else 5
            self.score += points
            self.score_label.config(text=f"Score: {self.score}")
            self.feedback_label.config(
                text=f"Correct! +{points} points",
                fg="#2e7d5b",
            )
            self.root.after(700, self.next_question)
            return True

        if self.attempt == 1:
            self.attempt = 2
            self.feedback_label.config(
                text="Wrong answer. Try once more (5 points).",
                fg="#b76e00",
            )
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()
            return False

        self.feedback_label.config(
            text=f"Incorrect. Correct answer was {self.answer}.",
            fg="#c0392b",
        )
        self.root.after(950, self.next_question)
        return False

    def displayResults(self):
        self.clear_frame()

        if self.score >= 90:
            grade = "A+"
        elif self.score >= 80:
            grade = "A"
        elif self.score >= 70:
            grade = "B"
        elif self.score >= 60:
            grade = "C"
        elif self.score >= 50:
            grade = "D"
        else:
            grade = "F"

        tk.Label(
            self.main_frame,
            text="Quiz Finished!",
            font=("Arial", 18, "bold"),
            bg="#a7c2e1",
            fg="#2b5b84",
        ).pack(pady=(10, 8))

        tk.Label(
            self.main_frame,
            text=f"Final Score: {self.score} / 100",
            font=("Arial", 14, "bold"),
            bg="#c2d5ea",
            fg="#172536",
        ).pack(pady=4)

        tk.Label(
            self.main_frame,
            text=f"Rank / Grade: {grade}",
            font=("Arial", 12, "bold"),
            bg="#eef4fb",
            fg="#2e7d5b",
        ).pack(pady=(0, 16))

        again = messagebox.askyesno(
            "Play Again",
            f"You scored {self.score}/100 ({grade}). Play again?",
        )

        if again:
            self.displayMenu()
        else:
            tk.Button(
                self.main_frame,
                text="Play Again",
                font=("Arial", 11, "bold"),
                bg="#2b5b84",
                fg="white",
                width=16,
                pady=6,
                command=self.displayMenu,
            ).pack(pady=5)

            tk.Button(
                self.main_frame,
                text="Exit",
                font=("Arial", 11, "bold"),
                bg="#c0392b",
                fg="white",
                width=16,
                pady=6,
                command=self.root.destroy,
            ).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = MathsQuizApp(root)
    root.mainloop()