"""
Student Database Management System
A CLI-based CRUD application using SQLite to manage student records with search, sort, and report generation.
"""

import sqlite3
import csv
import os
from datetime import datetime
from tabulate import tabulate  # pip install tabulate

DB_NAME = "students.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                semester INTEGER CHECK(semester BETWEEN 1 AND 8),
                cgpa REAL CHECK(cgpa BETWEEN 0 AND 10),
                email TEXT,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                subject TEXT NOT NULL,
                grade TEXT NOT NULL,
                marks REAL,
                semester INTEGER
            )
        """)
        conn.commit()


def add_student():
    print("\n➕ Add New Student")
    print("-" * 30)
    name = input("  Name: ").strip()
    roll_no = input("  Roll No: ").strip()
    dept = input("  Department: ").strip()
    try:
        sem = int(input("  Semester (1-8): "))
        cgpa = float(input("  CGPA (0-10): "))
    except ValueError:
        print("❌ Invalid input.")
        return
    email = input("  Email (optional): ").strip()
    phone = input("  Phone (optional): ").strip()

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO students (name, roll_no, department, semester, cgpa, email, phone) VALUES (?,?,?,?,?,?,?)",
                (name, roll_no, dept, sem, cgpa, email or None, phone or None)
            )
            conn.commit()
        print(f"\n✅ Student '{name}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"❌ Roll No '{roll_no}' already exists.")


def view_all_students(sort_by="name", order="ASC"):
    valid_cols = ["name", "roll_no", "department", "semester", "cgpa"]
    if sort_by not in valid_cols:
        sort_by = "name"

    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT id, name, roll_no, department, semester, cgpa FROM students ORDER BY {sort_by} {order}"
        ).fetchall()

    if not rows:
        print("\n  No students found.")
        return

    print(f"\n📋 All Students (sorted by {sort_by} {order})")
    print(tabulate(
        [dict(r) for r in rows],
        headers="keys",
        tablefmt="rounded_outline",
        floatfmt=".2f"
    ))
    print(f"\n  Total: {len(rows)} students")


def search_student():
    print("\n🔍 Search Student")
    print("  1. By Name\n  2. By Roll No\n  3. By Department\n  4. By CGPA range")
    choice = input("  Option: ").strip()

    query, params = "", ()
    if choice == "1":
        name = input("  Enter name (partial ok): ").strip()
        query = "SELECT * FROM students WHERE name LIKE ?"
        params = (f"%{name}%",)
    elif choice == "2":
        roll = input("  Enter Roll No: ").strip()
        query = "SELECT * FROM students WHERE roll_no = ?"
        params = (roll,)
    elif choice == "3":
        dept = input("  Enter Department: ").strip()
        query = "SELECT * FROM students WHERE department LIKE ?"
        params = (f"%{dept}%",)
    elif choice == "4":
        low = float(input("  Min CGPA: ") or 0)
        high = float(input("  Max CGPA: ") or 10)
        query = "SELECT * FROM students WHERE cgpa BETWEEN ? AND ?"
        params = (low, high)
    else:
        print("❌ Invalid option.")
        return

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    if not rows:
        print("  No students found.")
    else:
        print(tabulate([dict(r) for r in rows], headers="keys", tablefmt="rounded_outline", floatfmt=".2f"))


def update_student():
    roll = input("\n✏️  Enter Roll No to update: ").strip()
    with get_connection() as conn:
        student = conn.execute("SELECT * FROM students WHERE roll_no = ?", (roll,)).fetchone()
    if not student:
        print("❌ Student not found.")
        return

    print(f"\n  Found: {student['name']} | {student['department']} | Sem {student['semester']} | CGPA {student['cgpa']}")
    print("  What to update? (leave blank to skip)")

    updates = {}
    name = input(f"  Name [{student['name']}]: ").strip()
    dept = input(f"  Department [{student['department']}]: ").strip()
    sem = input(f"  Semester [{student['semester']}]: ").strip()
    cgpa = input(f"  CGPA [{student['cgpa']}]: ").strip()
    email = input(f"  Email [{student['email']}]: ").strip()

    if name: updates["name"] = name
    if dept: updates["department"] = dept
    if sem: updates["semester"] = int(sem)
    if cgpa: updates["cgpa"] = float(cgpa)
    if email: updates["email"] = email

    if not updates:
        print("  No changes made.")
        return

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    with get_connection() as conn:
        conn.execute(f"UPDATE students SET {set_clause} WHERE roll_no = ?", (*updates.values(), roll))
        conn.commit()
    print("✅ Student updated successfully!")


def delete_student():
    roll = input("\n🗑️  Enter Roll No to delete: ").strip()
    with get_connection() as conn:
        student = conn.execute("SELECT * FROM students WHERE roll_no = ?", (roll,)).fetchone()
    if not student:
        print("❌ Student not found.")
        return
    confirm = input(f"  Delete '{student['name']}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        with get_connection() as conn:
            conn.execute("DELETE FROM students WHERE roll_no = ?", (roll,))
            conn.commit()
        print("✅ Student deleted.")
    else:
        print("  Cancelled.")


def generate_report():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        avg_cgpa = conn.execute("SELECT AVG(cgpa) FROM students").fetchone()[0]
        dept_stats = conn.execute(
            "SELECT department, COUNT(*) as count, AVG(cgpa) as avg_cgpa, MAX(cgpa) as top_cgpa FROM students GROUP BY department"
        ).fetchall()
        sem_stats = conn.execute(
            "SELECT semester, COUNT(*) as count FROM students GROUP BY semester ORDER BY semester"
        ).fetchall()
        toppers = conn.execute(
            "SELECT name, roll_no, department, cgpa FROM students ORDER BY cgpa DESC LIMIT 5"
        ).fetchall()

    print("\n" + "=" * 55)
    print("  📊 STUDENT DATABASE REPORT")
    print("=" * 55)
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Total Students : {total}")
    print(f"  Average CGPA   : {avg_cgpa:.2f}" if avg_cgpa else "  No data")

    print("\n  Department-wise Stats:")
    print(tabulate([dict(r) for r in dept_stats], headers="keys", tablefmt="simple", floatfmt=".2f"))

    print("\n  Semester Distribution:")
    print(tabulate([dict(r) for r in sem_stats], headers="keys", tablefmt="simple"))

    print("\n  🏆 Top 5 Students by CGPA:")
    print(tabulate([dict(r) for r in toppers], headers="keys", tablefmt="simple", floatfmt=".2f"))


def export_csv():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM students").fetchall()
    if not rows:
        print("  No data to export.")
        return
    filename = f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows([dict(r) for r in rows])
    print(f"✅ Exported {len(rows)} records to '{filename}'")


def main():
    initialize_db()

    while True:
        print("\n" + "=" * 40)
        print("  🎓 Student Database System")
        print("=" * 40)
        print("  1. Add Student")
        print("  2. View All Students")
        print("  3. Search Student")
        print("  4. Update Student")
        print("  5. Delete Student")
        print("  6. Generate Report")
        print("  7. Export to CSV")
        print("  8. Exit")

        choice = input("\n  Enter choice: ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            sort = input("  Sort by (name/cgpa/semester/department) [name]: ").strip() or "name"
            order = input("  Order (ASC/DESC) [ASC]: ").strip().upper() or "ASC"
            view_all_students(sort, order)
        elif choice == "3":
            search_student()
        elif choice == "4":
            update_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            generate_report()
        elif choice == "7":
            export_csv()
        elif choice == "8":
            print("\n  Goodbye! 👋")
            break
        else:
            print("  ❌ Invalid choice.")


if __name__ == "__main__":
    main()
