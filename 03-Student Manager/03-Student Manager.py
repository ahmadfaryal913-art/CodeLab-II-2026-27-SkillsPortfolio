import os
import tkinter as tk
from tkinter import messagebox


class StudentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise 3 - Student Manager")
        self.root.geometry("840x610")
        self.root.configure(bg="#162232")

        self.set_icon()

        self.students = []
        self.file_path = self.find_data_file()
        self.load_students()

        self.main_frame = tk.Frame(self.root, bg="#162232", padx=18, pady=14)
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

    def build_student_record(self, student_id, name, cw1, cw2, cw3, exam):
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

        return self.build_student_record(student_id, name, cw1, cw2, cw3, exam)

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

    def save_students_to_file(self):
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(f"{len(self.students)}\n")
            for s in self.students:
                file.write(
                    f"{s['id']},{s['name']},{s['cw1']},{s['cw2']},{s['cw3']},{s['exam']}\n"
                )

    def build_ui(self):
        tk.Label(
            self.main_frame,
            text="Student Manager",
            font=("Tahoma", 18, "bold"),
            bg="#162232",
            fg="#f7be44",
        ).pack(pady=(0, 8))

        menu_row = tk.Frame(self.main_frame, bg="#162232")
        menu_row.pack(pady=(0, 8))

        tk.Button(
            menu_row,
            text="View All Students",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=17,
            pady=4,
            command=self.view_all_students,
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            menu_row,
            text="Highest Mark",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=14,
            pady=4,
            command=self.show_highest_student,
        ).grid(row=0, column=1, padx=3)

        tk.Button(
            menu_row,
            text="Lowest Mark",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=14,
            pady=4,
            command=self.show_lowest_student,
        ).grid(row=0, column=2, padx=3)

        tk.Button(
            menu_row,
            text="Sort High -> Low",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=16,
            pady=4,
            command=lambda: self.sort_students(descending=True),
        ).grid(row=0, column=3, padx=3)

        tk.Button(
            menu_row,
            text="Sort Low -> High",
            font=("Tahoma", 10, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=16,
            pady=4,
            command=lambda: self.sort_students(descending=False),
        ).grid(row=0, column=4, padx=3)

        search_row = tk.Frame(self.main_frame, bg="#162232")
        search_row.pack(pady=(0, 8))

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
            width=13,
            pady=3,
            command=self.view_individual_student,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            search_row,
            text="Delete Student",
            font=("Tahoma", 10, "bold"),
            bg="#d94e3f",
            fg="#ffffff",
            activebackground="#b83d30",
            activeforeground="#ffffff",
            width=14,
            pady=3,
            command=self.delete_student,
        ).pack(side="left")

        manage_box = tk.Frame(
            self.main_frame,
            bg="#1f2f44",
            bd=1,
            relief="solid",
            padx=10,
            pady=8,
        )
        manage_box.pack(fill="x", pady=(0, 10))

        tk.Label(
            manage_box,
            text="ID:",
            font=("Tahoma", 9, "bold"),
            bg="#1f2f44",
            fg="#ffffff",
        ).grid(row=0, column=0, padx=(0, 3))
        self.id_entry = tk.Entry(manage_box, font=("Tahoma", 9), width=8, bg="#fdfbf7", fg="#162232")
        self.id_entry.grid(row=0, column=1, padx=(0, 8))

        tk.Label(
            manage_box,
            text="Name:",
            font=("Tahoma", 9, "bold"),
            bg="#1f2f44",
            fg="#ffffff",
        ).grid(row=0, column=2, padx=(0, 3))
        self.name_entry = tk.Entry(manage_box, font=("Tahoma", 9), width=15, bg="#fdfbf7", fg="#162232")
        self.name_entry.grid(row=0, column=3, padx=(0, 8))

        tk.Label(
            manage_box,
            text="CW1:",
            font=("Tahoma", 9, "bold"),
            bg="#1f2f44",
            fg="#ffffff",
        ).grid(row=0, column=4, padx=(0, 2))
        self.cw1_entry = tk.Entry(manage_box, font=("Tahoma", 9), width=5, bg="#fdfbf7", fg="#162232")
        self.cw1_entry.grid(row=0, column=5, padx=(0, 6))

        tk.Label(
            manage_box,
            text="CW2:",
            font=("Tahoma", 9, "bold"),
            bg="#1f2f44",
            fg="#ffffff",
        ).grid(row=0, column=6, padx=(0, 2))
        self.cw2_entry = tk.Entry(manage_box, font=("Tahoma", 9), width=5, bg="#fdfbf7", fg="#162232")
        self.cw2_entry.grid(row=0, column=7, padx=(0, 6))

        tk.Label(
            manage_box,
            text="CW3:",
            font=("Tahoma", 9, "bold"),
            bg="#1f2f44",
            fg="#ffffff",
        ).grid(row=0, column=8, padx=(0, 2))
        self.cw3_entry = tk.Entry(manage_box, font=("Tahoma", 9), width=5, bg="#fdfbf7", fg="#162232")
        self.cw3_entry.grid(row=0, column=9, padx=(0, 6))

        tk.Label(
            manage_box,
            text="Exam:",
            font=("Tahoma", 9, "bold"),
            bg="#1f2f44",
            fg="#ffffff",
        ).grid(row=0, column=10, padx=(0, 2))
        self.exam_entry = tk.Entry(manage_box, font=("Tahoma", 9), width=6, bg="#fdfbf7", fg="#162232")
        self.exam_entry.grid(row=0, column=11, padx=(0, 8))

        tk.Button(
            manage_box,
            text="Add Student",
            font=("Tahoma", 9, "bold"),
            bg="#f7be44",
            fg="#000000",
            activebackground="#dea62b",
            activeforeground="#000000",
            width=11,
            command=self.add_student,
        ).grid(row=0, column=12, padx=3)

        tk.Button(
            manage_box,
            text="Update Student",
            font=("Tahoma", 9, "bold"),
            bg="#2b6cb0",
            fg="#ffffff",
            activebackground="#22568c",
            activeforeground="#ffffff",
            width=13,
            command=self.update_student,
        ).grid(row=0, column=13, padx=3)

        self.output_box = tk.Text(
            self.main_frame,
            height=16,
            width=92,
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

    def display_student_table(self, records, title_note=""):
        if not records:
            self.write_output("No student records found.")
            return

        lines = []
        if title_note:
            lines.append(title_note)
        lines.append(
            f"{'ID':<8} {'Name':<18} {'CW Sum':<8} {'Exam':<7} {'Total':<8} {'%':<8} {'Grade':<6}"
        )
        lines.append("-" * 74)

        total_pct = 0
        for s in records:
            total_pct += s["percentage"]
            lines.append(
                f"{s['id']:<8} {s['name']:<18} {s['cw_total']:<8} {s['exam']:<7} {s['total']:<8} {s['percentage']:<8} {s['grade']:<6}"
            )

        avg_pct = round(total_pct / len(records), 2)
        lines.append("-" * 74)
        lines.append(f"Total Students: {len(records)}   |   Average Percentage: {avg_pct}%")
        self.write_output("\n".join(lines))

    def view_all_students(self):
        self.display_student_table(self.students)

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

    def sort_students(self, descending=True):
        if not self.students:
            self.write_output("No student records to sort.")
            return

        sorted_list = sorted(
            self.students,
            key=lambda item: item["total"],
            reverse=descending,
        )
        order_label = "Sorted by Overall Marks (High to Low)" if descending else "Sorted by Overall Marks (Low to High)"
        self.display_student_table(sorted_list, title_note=order_label)

    def read_form_inputs(self):
        student_id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()

        if not student_id or not name:
            messagebox.showwarning("Missing Fields", "Please enter both Student ID and Name.")
            return None

        try:
            cw1 = int(self.cw1_entry.get().strip())
            cw2 = int(self.cw2_entry.get().strip())
            cw3 = int(self.cw3_entry.get().strip())
            exam = int(self.exam_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Marks", "CW1, CW2, CW3, and Exam must be whole numbers.")
            return None

        if not (0 <= cw1 <= 20 and 0 <= cw2 <= 20 and 0 <= cw3 <= 20 and 0 <= exam <= 100):
            messagebox.showwarning("Out of Range", "Coursework marks must be 0-20 and Exam must be 0-100.")
            return None

        return self.build_student_record(student_id, name, cw1, cw2, cw3, exam)

    def clear_form_inputs(self):
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.cw1_entry.delete(0, tk.END)
        self.cw2_entry.delete(0, tk.END)
        self.cw3_entry.delete(0, tk.END)
        self.exam_entry.delete(0, tk.END)

    def add_student(self):
        new_student = self.read_form_inputs()
        if not new_student:
            return

        for existing in self.students:
            if existing["id"].lower() == new_student["id"].lower():
                messagebox.showwarning("Duplicate ID", f"Student ID '{new_student['id']}' already exists.")
                return

        self.students.append(new_student)
        self.save_students_to_file()
        self.clear_form_inputs()
        self.view_all_students()
        messagebox.showinfo("Added", f"Added {new_student['name']} and saved to studentMarks.txt.")

    def update_student(self):
        updated_student = self.read_form_inputs()
        if not updated_student:
            return

        for index, existing in enumerate(self.students):
            if existing["id"].lower() == updated_student["id"].lower():
                self.students[index] = updated_student
                self.save_students_to_file()
                self.clear_form_inputs()
                self.view_all_students()
                messagebox.showinfo("Updated", f"Updated record for ID '{updated_student['id']}'.")
                return

        messagebox.showwarning("Not Found", f"No student found with ID '{updated_student['id']}'.")

    def delete_student(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            query = self.id_entry.get().strip().lower()

        if not query:
            messagebox.showwarning("Missing ID or Name", "Enter a Student ID or Name in the search box to delete.")
            return

        for index, s in enumerate(self.students):
            if s["id"].lower() == query or s["name"].lower() == query:
                removed = self.students.pop(index)
                self.save_students_to_file()
                self.search_entry.delete(0, tk.END)
                self.view_all_students()
                messagebox.showinfo("Deleted", f"Deleted {removed['name']} ({removed['id']}).")
                return

        messagebox.showwarning("Not Found", "No matching student record found to delete.")


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()