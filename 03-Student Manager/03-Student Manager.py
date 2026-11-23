import os
import tkinter as tk
from tkinter import messagebox


class StudentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise 3 - Student Manager")
        self.root.geometry("760x520")
        self.root.configure(bg="#162232")

        self.set_icon()

        self.students = []
        self.file_path = self.find_data_file()
        self.load_students()

        self.main_frame = tk.Frame(self.root, bg="#162232", padx=18, pady=16)
        self.main_frame.pack(fill="both", expand=True)

        self.show_part1_overview()

    def set_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "calculator_149699.ico")

        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass

    def find_data_file(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, "studentMarks.txt"),
            os.path.join(base_dir, "resources", "studentMarks.txt"),
            os.path.join(base_dir, "..", "resources", "studentMarks.txt"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return os.path.join(base_dir, "studentMarks.txt")

    def calculate_grade(self, percentage):
        if percentage >= 70:
            return "A"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"

    def parse_student_line(self, line):
        # Expected format: StudentCode,Name,Coursework1,Coursework2,Coursework3,Exam
        # Also supports pipe '|' or comma ',' separated lines cleanly
        if "|" in line:
            parts = [item.strip() for item in line.split("|")]
        else:
            parts = [item.strip() for item in line.split(",")]

        if len(parts) < 6:
            return None

        student_id = parts[0]
        name = parts[1]

        try:
            cw1 = int(parts[2])
            cw2 = int(parts[3])
            cw3 = int(parts[4])
            exam = int(parts[5])
        except ValueError:
            return None

        coursework_total = cw1 + cw2 + cw3
        overall_total = coursework_total + exam
        max_marks = 160
        percentage = round((overall_total / max_marks) * 100, 2)
        grade = self.calculate_grade(percentage)

        return {
            "id": student_id,
            "name": name,
            "cw1": cw1,
            "cw2": cw2,
            "cw3": cw3,
            "cw_total": coursework_total,
            "exam": exam,
            "total": overall_total,
            "percentage": percentage,
            "grade": grade,
        }

    def load_students(self):
        self.students = []
        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            first_line = True
            for line in file:
                clean_line = line.strip()
                if not clean_line:
                    continue

                # If the first line is a count (e.g., "10"), skip it safely
                if first_line and clean_line.isdigit():
                    first_line = False
                    continue
                first_line = False

                student = self.parse_student_line(clean_line)
                if student:
                    self.students.append(student)

    def show_part1_overview(self):
        tk.Label(
            self.main_frame,
            text="Student Manager - Part 1 (Data Loader)",
            font=("Tahoma", 17, "bold"),
            bg="#162232",
            fg="#f7be44",
        ).pack(pady=(0, 6))

        tk.Label(
            self.main_frame,
            text=f"Loaded Students: {len(self.students)}  |  File: {os.path.basename(self.file_path)}",
            font=("Tahoma", 10, "bold"),
            bg="#162232",
            fg="#8fd3ff",
        ).pack(pady=(0, 12))

        display_box = tk.Text(
            self.main_frame,
            height=18,
            width=84,
            font=("Consolas", 10),
            bg="#fdfbf7",
            fg="#162232",
            padx=10,
            pady=10,
        )
        display_box.pack(fill="both", expand=True)

        if not self.students:
            display_box.insert(
                tk.END,
                "No student records found in studentMarks.txt.\n"
                "Format expected per line: ID,Name,CW1,CW2,CW3,Exam\n"
                "Example: 1345,John Curry,8,15,7,45",
            )
        else:
            display_box.insert(
                tk.END,
                f"{'ID':<8} {'Name':<18} {'CW Total':<10} {'Exam':<8} {'Total':<8} {'%':<8} {'Grade':<6}\n",
            )
            display_box.insert(tk.END, "-" * 76 + "\n")
            for s in self.students:
                display_box.insert(
                    tk.END,
                    f"{s['id']:<8} {s['name']:<18} {s['cw_total']:<10} {s['exam']:<8} {s['total']:<8} {s['percentage']:<8} {s['grade']:<6}\n",
                )

        display_box.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()