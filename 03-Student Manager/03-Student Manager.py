import os
import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class StudentManagerApp:
    """Interactive Tkinter Student Manager with Home view, CRUD operations, and Pillow background."""

    BG_IMAGE_FILENAME = "exercise 3 background.avif"
    ICON_FILENAME = "calculator_149699.ico"
    COURSEWORK_MAX = 60
    EXAM_MAX = 100
    OVERALL_MAX = 160

    # Consistent portfolio theme palette
    BG_DARK = "#162232"
    PANEL_DARK = "#1e2e42"
    CARD_LIGHT = "#fdfbf7"
    ACCENT_GOLD = "#f7be44"
    ACCENT_GOLD_HOVER = "#e5ac2e"
    ACTION_BLUE = "#2b6cb0"
    ACTION_BLUE_HOVER = "#22568c"
    DANGER_BG = "#c0392b"
    DANGER_HOVER = "#9e2d21"
    TEXT_LIGHT = "#ffffff"
    TEXT_MUTED = "#b8c7d9"
    TEXT_DARK = "#162232"

    FONT_FAMILY = "Tahoma"
    MONO_FONT = "Consolas"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Exercise 3 - Student Manager")
        self.root.geometry("920x650")
        self.root.minsize(820, 560)
        self.root.configure(bg=self.BG_DARK)

        self.set_icon()

        # Background image state
        self._bg_source_image = None
        self._bg_photo_image = None
        self._resize_after_id = None
        self.bg_label = tk.Label(self.root, bg=self.BG_DARK)
        self.bg_label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.load_background_image()

        # Student data state
        self.students = []
        self.file_path = self.find_data_file()
        self.load_students()

        self.main_frame = tk.Frame(
            self.root,
            bg=self.BG_DARK,
            padx=18,
            pady=14,
            highlightbackground=self.ACCENT_GOLD,
            highlightthickness=1,
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.90)

        self.root.bind("<Configure>", self.on_window_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.displayHome()

    def set_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, self.ICON_FILENAME)

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

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def on_close(self):
        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except ValueError:
                pass
        self.root.destroy()

    # ------------------------------------------------------------------
    # Data Loading, Calculation & Persistence
    # ------------------------------------------------------------------

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
        if percentage >= 60:
            return "B"
        if percentage >= 50:
            return "C"
        if percentage >= 40:
            return "D"
        return "F"

    def build_student_record(self, student_id, name, cw1, cw2, cw3, exam):
        coursework_total = cw1 + cw2 + cw3
        overall_total = coursework_total + exam
        percentage = round((overall_total / self.OVERALL_MAX) * 100, 2)
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

    def _class_average_percentage(self):
        if not self.students:
            return 0.0
        return round(sum(s["percentage"] for s in self.students) / len(self.students), 2)

    # ------------------------------------------------------------------
    # Navigation & UI Builders
    # ------------------------------------------------------------------

    def displayHome(self):
        """Render the Home overview screen for Student Manager."""
        self.clear_frame()

        tk.Label(
            self.main_frame,
            text="STUDENT MANAGER STUDIO",
            font=(self.FONT_FAMILY, 22, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(pady=(12, 4))

        tk.Label(
            self.main_frame,
            text="Code Lab 2 • Coursework, Exam & Grade Record System",
            font=(self.FONT_FAMILY, 10),
            bg=self.BG_DARK,
            fg=self.TEXT_MUTED,
        ).pack(pady=(0, 16))

        overview_card = tk.Frame(
            self.main_frame,
            bg=self.PANEL_DARK,
            padx=22,
            pady=16,
            highlightbackground="#2b405c",
            highlightthickness=1,
        )
        overview_card.pack(fill="x", pady=8)

        features = [
            f"• Loaded {len(self.students)} student records  |  Class Average: {self._class_average_percentage()}%",
            f"• Grading out of {self.OVERALL_MAX} (CW1–CW3 out of {self.COURSEWORK_MAX} + Exam out of {self.EXAM_MAX})",
            "• View all records, inspect top/lowest scorers, sort marks, and add/update/delete entries",
        ]
        for line in features:
            tk.Label(
                overview_card,
                text=line,
                font=(self.FONT_FAMILY, 10),
                bg=self.PANEL_DARK,
                fg=self.TEXT_LIGHT,
                anchor="w",
            ).pack(fill="x", pady=3)

        tk.Button(
            self.main_frame,
            text="Open Student Manager →",
            font=(self.FONT_FAMILY, 12, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=24,
            pady=9,
            command=self.open_manager,
        ).pack(pady=(16, 10))

        tk.Button(
            self.main_frame,
            text="Exit Application",
            font=(self.FONT_FAMILY, 10),
            bg=self.PANEL_DARK,
            fg=self.TEXT_MUTED,
            activebackground="#273b54",
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=18,
            pady=5,
            command=self.on_close,
        ).pack()

    def open_manager(self):
        """Switch to the main Student Manager workspace and load all records."""
        self.build_ui()
        self.view_all_students()

    def build_ui(self):
        """Build the Student Manager workspace with a top Home navigation button."""
        self.clear_frame()

        top_bar = tk.Frame(self.main_frame, bg=self.BG_DARK)
        top_bar.pack(fill="x", pady=(0, 8))

        tk.Button(
            top_bar,
            text="← Home",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.ACCENT_GOLD,
            activebackground="#273b54",
            activeforeground=self.ACCENT_GOLD,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.displayHome,
        ).pack(side="left")

        tk.Label(
            top_bar,
            text="Student Manager",
            font=(self.FONT_FAMILY, 18, "bold"),
            bg=self.BG_DARK,
            fg=self.ACCENT_GOLD,
        ).pack(side="left", padx=(14, 0))

        menu_row = tk.Frame(self.main_frame, bg=self.BG_DARK)
        menu_row.pack(pady=(0, 8))

        tk.Button(
            menu_row,
            text="View All Students",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACTION_BLUE,
            fg=self.TEXT_LIGHT,
            activebackground=self.ACTION_BLUE_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=17,
            pady=4,
            command=self.view_all_students,
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            menu_row,
            text="Highest Mark",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACTION_BLUE,
            fg=self.TEXT_LIGHT,
            activebackground=self.ACTION_BLUE_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=14,
            pady=4,
            command=self.show_highest_student,
        ).grid(row=0, column=1, padx=3)

        tk.Button(
            menu_row,
            text="Lowest Mark",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACTION_BLUE,
            fg=self.TEXT_LIGHT,
            activebackground=self.ACTION_BLUE_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=14,
            pady=4,
            command=self.show_lowest_student,
        ).grid(row=0, column=2, padx=3)

        tk.Button(
            menu_row,
            text="Sort High -> Low",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACTION_BLUE,
            fg=self.TEXT_LIGHT,
            activebackground=self.ACTION_BLUE_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=16,
            pady=4,
            command=lambda: self.sort_students(descending=True),
        ).grid(row=0, column=3, padx=3)

        tk.Button(
            menu_row,
            text="Sort Low -> High",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACTION_BLUE,
            fg=self.TEXT_LIGHT,
            activebackground=self.ACTION_BLUE_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=16,
            pady=4,
            command=lambda: self.sort_students(descending=False),
        ).grid(row=0, column=4, padx=3)

        search_row = tk.Frame(self.main_frame, bg=self.BG_DARK)
        search_row.pack(pady=(0, 8))

        tk.Label(
            search_row,
            text="Student ID or Name:",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.BG_DARK,
            fg=self.TEXT_LIGHT,
        ).pack(side="left", padx=(0, 6))

        self.search_entry = tk.Entry(
            search_row,
            font=(self.FONT_FAMILY, 10),
            width=22,
            bg=self.CARD_LIGHT,
            fg=self.TEXT_DARK,
        )
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<Return>", lambda _event: self.view_individual_student())

        tk.Button(
            search_row,
            text="View Student",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=13,
            pady=3,
            command=self.view_individual_student,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            search_row,
            text="Delete Student",
            font=(self.FONT_FAMILY, 10, "bold"),
            bg=self.DANGER_BG,
            fg=self.TEXT_LIGHT,
            activebackground=self.DANGER_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=14,
            pady=3,
            command=self.delete_student,
        ).pack(side="left")

        manage_box = tk.Frame(
            self.main_frame,
            bg=self.PANEL_DARK,
            bd=1,
            relief="solid",
            padx=10,
            pady=8,
        )
        manage_box.pack(fill="x", pady=(0, 10))

        tk.Label(
            manage_box,
            text="ID:",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).grid(row=0, column=0, padx=(0, 3))
        self.id_entry = tk.Entry(manage_box, font=(self.FONT_FAMILY, 9), width=8, bg=self.CARD_LIGHT, fg=self.TEXT_DARK)
        self.id_entry.grid(row=0, column=1, padx=(0, 8))

        tk.Label(
            manage_box,
            text="Name:",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).grid(row=0, column=2, padx=(0, 3))
        self.name_entry = tk.Entry(manage_box, font=(self.FONT_FAMILY, 9), width=15, bg=self.CARD_LIGHT, fg=self.TEXT_DARK)
        self.name_entry.grid(row=0, column=3, padx=(0, 8))

        tk.Label(
            manage_box,
            text="CW1:",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).grid(row=0, column=4, padx=(0, 2))
        self.cw1_entry = tk.Entry(manage_box, font=(self.FONT_FAMILY, 9), width=5, bg=self.CARD_LIGHT, fg=self.TEXT_DARK)
        self.cw1_entry.grid(row=0, column=5, padx=(0, 6))

        tk.Label(
            manage_box,
            text="CW2:",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).grid(row=0, column=6, padx=(0, 2))
        self.cw2_entry = tk.Entry(manage_box, font=(self.FONT_FAMILY, 9), width=5, bg=self.CARD_LIGHT, fg=self.TEXT_DARK)
        self.cw2_entry.grid(row=0, column=7, padx=(0, 6))

        tk.Label(
            manage_box,
            text="CW3:",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).grid(row=0, column=8, padx=(0, 2))
        self.cw3_entry = tk.Entry(manage_box, font=(self.FONT_FAMILY, 9), width=5, bg=self.CARD_LIGHT, fg=self.TEXT_DARK)
        self.cw3_entry.grid(row=0, column=9, padx=(0, 6))

        tk.Label(
            manage_box,
            text="Exam:",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.PANEL_DARK,
            fg=self.TEXT_LIGHT,
        ).grid(row=0, column=10, padx=(0, 2))
        self.exam_entry = tk.Entry(manage_box, font=(self.FONT_FAMILY, 9), width=6, bg=self.CARD_LIGHT, fg=self.TEXT_DARK)
        self.exam_entry.grid(row=0, column=11, padx=(0, 8))

        tk.Button(
            manage_box,
            text="Add Student",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.ACCENT_GOLD,
            fg=self.TEXT_DARK,
            activebackground=self.ACCENT_GOLD_HOVER,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            cursor="hand2",
            width=11,
            command=self.add_student,
        ).grid(row=0, column=12, padx=3)

        tk.Button(
            manage_box,
            text="Update Student",
            font=(self.FONT_FAMILY, 9, "bold"),
            bg=self.ACTION_BLUE,
            fg=self.TEXT_LIGHT,
            activebackground=self.ACTION_BLUE_HOVER,
            activeforeground=self.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            width=13,
            command=self.update_student,
        ).grid(row=0, column=13, padx=3)

        self.output_box = tk.Text(
            self.main_frame,
            height=16,
            width=92,
            font=(self.MONO_FONT, 10),
            bg=self.CARD_LIGHT,
            fg=self.TEXT_DARK,
            padx=12,
            pady=10,
        )
        self.output_box.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Reporting, Search, Sorting & CRUD Operations
    # ------------------------------------------------------------------

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
            f"CW Total      : {s['cw_total']} / {self.COURSEWORK_MAX}\n"
            f"Exam Mark     : {s['exam']} / {self.EXAM_MAX}\n"
            f"Overall Total : {s['total']} / {self.OVERALL_MAX}\n"
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
        order_label = (
            "Sorted by Overall Marks (High to Low)"
            if descending
            else "Sorted by Overall Marks (Low to High)"
        )
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