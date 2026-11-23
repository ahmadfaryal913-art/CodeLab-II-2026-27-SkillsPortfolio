import os
import tkinter as tk
from tkinter import messagebox


class StudentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise 3 - Student Manager")
        self.root.geometry("800x540")
        self.root.configure(bg="#162232")

        self.set_icon()

        self.students = []
        self.file_path = self.find_data_file()
        self.load_students()

        self.main_frame = tk.Frame(self.root, bg="#162232", padx=18, pady=16)
        self.main_frame.pack(fill="both", expand=True)

        self.build_ui()
        self.view_all_students()

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

                if first_line and clean_line.isdigit():
                    first_line = False
                    continue
                first_line = False

                student = self.parse_student_line(clean_line)
                if student:
                    self.students.append(student)

    def build_ui(self):
        tk.Label(
            self.main_frame,
            text="Student Manager",
            font=("Tahoma", 18, "bold"),
            bg="#162232",
            fg="#f7be44",
        ).pack(pady=(0, 8))

        menu_row = tk.Frame(self.main_frame, bg="#162232")
        menu_row.pack(pady=(0, 10))

        tk.Button(
            menu_row,
            text="View All Students",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=18,
            pady=5,
            command=self.view_all_students,
        ).grid(row=0, column=0, padx=4)

        tk.Button(
            menu_row,
            text="Highest Mark",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=16,
            pady=5,
            command=self.show_highest_student,
        ).grid(row=0, column=1, padx=4)

        tk.Button(
            menu_row,
            text="Lowest Mark",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=16,
            pady=5,
            command=self.show_lowest_student,
        ).grid(row=0, column=2, padx=4)

        search_row = tk.Frame(self.main_frame, bg="#162232")
        search_row.pack(pady=(0, 12))

        tk.Label(
            search_row,
            text="Student ID or Name:",
            font=("Tahoma", 10, "bold"),
            bg="#162232",
            fg="#ffffff",
        ).pack(side="left", padx=(0, 6))

        self.search_entry = tk.Entry(
            search_row,
            font=("Tahoma", 10),
            width=22,
            bg="#fdfbf7",
            fg="#162232",
        )
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<Return>", lambda event: self.view_individual_student())

        tk.Button(
            search_row,
            text="View Student",
            font=("Tahoma", 10, "bold"),
            bg="#f7be44",
            fg="#000000",
            activebackground="#dea62b",
            activeforeground="#000000",
            width=14,
            pady=4,
            command=self.view_individual_student,
        ).pack(side="left")

        self.output_box = tk.Text(
            self.main_frame,
            height=17,
            width=88,
            font=("Consolas", 10),
            bg="#fdfbf7",
            fg="#162232",
            padx=12,
            pady=10,
        )
        self.output_box.pack(fill="both", expand=True)

    def write_output(self, text):
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.config(state="disabled")

    def format_student_detail(self, s):
        return (
            f"Name          : {s['name']}\n"
            f"Student ID    : {s['id']}\n"
            f"Coursework 1  : {s['cw1']}\n"
            f"Coursework 2  : {s['cw2']}\n"
            f"Coursework 3  : {s['cw3']}\n"
            f"CW Total      : {s['cw_total']} / 60\n"
            f"Exam Mark     : {s['exam']} / 100\n"
            f"Overall Total : {s['total']} / 160\n"
            f"Percentage    : {s['percentage']}%\n"
            f"Grade         : {s['grade']}\n"
        )

    def view_all_students(self):
        if not self.students:
            self.write_output("No student records found in studentMarks.txt.")
            return

        lines = []
        lines.append(
            f"{'ID':<8} {'Name':<18} {'CW Sum':<8} {'Exam':<7} {'Total':<8} {'%':<8} {'Grade':<6}"
        )
        lines.append("-" * 74)

        total_pct = 0
        for s in self.students:
            total_pct += s["percentage"]
            lines.append(
                f"{s['id']:<8} {s['name']:<18} {s['cw_total']:<8} {s['exam']:<7} {s['total']:<8} {s['percentage']:<8} {s['grade']:<6}"
            )

        avg_pct = round(total_pct / len(self.students), 2)
        lines.append("-" * 74)
        lines.append(f"Total Students: {len(self.students)}   |   Average Percentage: {avg_pct}%")
        self.write_output("\n".join(lines))

    def view_individual_student(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Missing Input", "Please enter a student ID or name.")
            return

        matches = [
            s
            for s in self.students
            if s["id"].lower() == query or query in s["name"].lower()
        ]

        if not matches:
            self.write_output(f"No student found matching '{self.search_entry.get().strip()}'.")
            return

        if len(matches) == 1:
            self.write_output(
                "STUDENT RECORD\n" + "=" * 35 + "\n" + self.format_student_detail(matches[0])
            )
        else:
            blocks = ["MATCHING STUDENTS\n" + "=" * 35]
            for s in matches:
                blocks.append(self.format_student_detail(s) + "-" * 35)
            self.write_output("\n".join(blocks))

    def show_highest_student(self):
        if not self.students:
            self.write_output("No student records available.")
            return

        top_student = max(self.students, key=lambda item: item["total"])
        self.write_output(
            "HIGHEST OVERALL MARK\n"
            + "=" * 35
            + "\n"
            + self.format_student_detail(top_student)
        )

    def show_lowest_student(self):
        if not self.students:
            self.write_output("No student records available.")
            return

        low_student = min(self.students, key=lambda item: item["total"])
        self.write_output(
            "LOWEST OVERALL MARK\n"
            + "=" * 35
            + "\n"
            + self.format_student_detail(low_student)
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()