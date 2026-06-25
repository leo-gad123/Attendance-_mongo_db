from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from pymongo import MongoClient

# =========================
# DATABASE CONNECTION
# =========================

try:
    client = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=5000
    )
    client.server_info()

    db = client["attendance_db"]
    attendance = db["attendance"]

except Exception as e:
    messagebox.showerror(
        "Database Error",
        f"Could not connect to MongoDB\n\n{e}"
    )
    exit()


# =========================
# FUNCTIONS
# =========================

def current_date():
    return datetime.now().strftime("%Y-%m-%d")


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def clear_fields():
    emp_id_var.set("")
    name_var.set("")


def check_in():
    emp_id = emp_id_var.get().strip()
    name = name_var.get().strip()

    if not emp_id or not name:
        messagebox.showwarning(
            "Input Error",
            "Employee ID and Name are required."
        )
        return

    record = attendance.find_one({
        "emp_id": emp_id,
        "date": current_date()
    })

    if record:
        messagebox.showwarning(
            "Already Checked In",
            "Employee has already checked in today."
        )
        return

    attendance.insert_one({
        "emp_id": emp_id,
        "name": name,
        "date": current_date(),
        "check_in": current_time(),
        "check_out": None
    })

    messagebox.showinfo(
        "Success",
        "Check-in completed successfully."
    )

    clear_fields()


def check_out():
    emp_id = emp_id_var.get().strip()

    if not emp_id:
        messagebox.showwarning(
            "Input Error",
            "Enter Employee ID."
        )
        return

    result = attendance.update_one(
        {
            "emp_id": emp_id,
            "date": current_date(),
            "check_out": None
        },
        {
            "$set": {
                "check_out": current_time()
            }
        }
    )

    if result.modified_count:
        messagebox.showinfo(
            "Success",
            "Check-out completed successfully."
        )
        clear_fields()
    else:
        messagebox.showwarning(
            "Not Found",
            "No active check-in found."
        )


def view_records():
    window = Toplevel(root)
    window.title("Attendance Records")
    window.geometry("900x400")

    columns = (
        "Employee ID",
        "Name",
        "Date",
        "Check In",
        "Check Out"
    )

    tree = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    scrollbar = Scrollbar(
        window,
        orient=VERTICAL,
        command=tree.yview
    )

    tree.configure(yscroll=scrollbar.set)

    tree.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    records = attendance.find().sort("_id", -1)

    for record in records:
        tree.insert(
            "",
            END,
            values=(
                record.get("emp_id", ""),
                record.get("name", ""),
                record.get("date", ""),
                record.get("check_in", ""),
                record.get("check_out", "")
            )
        )


# =========================
# GUI
# =========================

root = Tk()
root.title("Employee Attendance System")
root.geometry("450x300")
root.resizable(False, False)

emp_id_var = StringVar()
name_var = StringVar()

title = Label(
    root,
    text="Employee Attendance System",
    font=("Arial", 16, "bold")
)
title.pack(pady=15)

Label(
    root,
    text="Employee ID"
).pack()

Entry(
    root,
    textvariable=emp_id_var,
    width=35
).pack(pady=5)

Label(
    root,
    text="Employee Name"
).pack()

Entry(
    root,
    textvariable=name_var,
    width=35
).pack(pady=5)

Button(
    root,
    text="Check In",
    width=20,
    command=check_in
).pack(pady=5)

Button(
    root,
    text="Check Out",
    width=20,
    command=check_out
).pack(pady=5)

Button(
    root,
    text="View Records",
    width=20,
    command=view_records
).pack(pady=5)

Button(
    root,
    text="Exit",
    width=20,
    command=root.destroy
).pack(pady=5)

root.mainloop()