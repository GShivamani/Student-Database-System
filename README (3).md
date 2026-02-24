# 🎓 Student Database Management System

> A fully-featured CLI CRUD app backed by SQLite — manage student records with search, filtering, GPA reports, and CSV export.

---

## 📌 Description

A terminal-based student record system using SQLite and Python. Supports full CRUD operations, multi-field search, department/semester-wise reports, CGPA-based filtering, and CSV export — covering core DBMS concepts hands-on.

---

## 🛠️ Tech Stack

- Python 3.x
- SQLite3 (built-in)
- `tabulate` for table formatting

---

## 🚀 Getting Started

```bash
git clone https://github.com/yourusername/student-db.git
cd student-db
pip install tabulate
python student_db.py
```

---

## 💻 Features

| Feature | Details |
|---|---|
| Add Student | Name, Roll No, Dept, Semester, CGPA, Email, Phone |
| View All | Sortable by any field, ASC/DESC |
| Search | By name, roll no, department, or CGPA range |
| Update | Partial updates — skip fields you don't want to change |
| Delete | With confirmation prompt |
| Reports | Dept-wise stats, semester distribution, top 5 students |
| Export | CSV export with timestamp |

---

## 📂 Project Structure

```
student-db/
├── student_db.py       # Main application
├── students.db         # Auto-created SQLite database
├── students_export_*.csv  # Generated exports
└── README.md
```

---

## 🧠 Concepts Covered

- Relational databases with SQLite
- SQL: SELECT, INSERT, UPDATE, DELETE, JOIN, GROUP BY
- Foreign key constraints and CASCADE delete
- CLI application design
- CSV I/O in Python

---

## 🗃️ Database Schema

```sql
students(id, name, roll_no, department, semester, cgpa, email, phone, created_at)
grades(id, student_id, subject, grade, marks, semester)
```

---

## 📄 License

MIT
