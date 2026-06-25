    from tkinter import *
    from tkinter import messagebox
    from datetime import datetime
    from pymongo import MongoClient

    # ================= DATABASE =================

    client = MongoClient("mongodb://localhost:27017/")
    db = client["attendance_db"]
    attendance = db["attendance"]

    # ================= FUNCTIONS =================

    def get_today():
        return datetime.now().strftime("%Y-%m-%d")

    def check_in():
        emp_id = emp_id_entry.get().strip()
        name = name_entry.get().strip()

        if not emp_id or not name:
            messagebox.showwarning("Error", "Enter Employee ID and Name")
            return

        today = get_today()

        existing = attendance.find_one({
            "emp_id": emp_id,
            "date": today
        })

        if existing:
            messagebox.showwarning("Warning", "Already checked in today!")
            return

        attendance.insert_one({
            "emp_id": emp_id,
            "name": name,
            "date": today,
            "check_in": datetime.now().strftime("%H:%M:%S"),
            "check_out": None
        })

        messagebox.showinfo("Success", "Check-in successful!")

    def check_out():
        emp_id = emp_id_entry.get().strip()

        if not emp_id:
            messagebox.showwarning("Error", "Enter Employee ID")
            return

        result = attendance.update_one(
            {
                "emp_id": emp_id,
                "date": get_today(),
                "check_out": None
            },
            {
                "$set": {
                    "check_out": datetime.now().strftime("%H:%M:%S")
                }
            }
        )

        if result.modified_count:
            messagebox.showinfo("Success", "Check-out successful!")
        else:
            messagebox.showwarning(
                "Warning",
                "No check-in found or already checked out"
            )

    def view_records():
        top = Toplevel(root)
        top.title("Attendance Records")
        top.geometry("700x400")

        text = Text(top)
        text.pack(fill=BOTH, expand=True)

        records = attendance.find().sort("_id", -1)

        for r in records:
            text.insert(
                END,
                f"EMP:{r['emp_id']} | "
                f"NAME:{r['name']} | "
                f"DATE:{r['date']} | "
                f"IN:{r.get('check_in','')} | "
                f"OUT:{r.get('check_out','')}\n"
            )

    # ================= UI =================

    root = Tk()
    root.title("Attendance System")
    root.geometry("500x350")

    Label(root, text="Employee ID").pack()
    emp_id_entry = Entry(root, width=30)
    emp_id_entry.pack(pady=5)

    Label(root, text="Employee Name").pack()
    name_entry = Entry(root, width=30)
    name_entry.pack(pady=5)

    Button(root, text="Check In",
        command=check_in).pack(pady=5)

    Button(root, text="Check Out",
        command=check_out).pack(pady=5)

    Button(root, text="View Records",
        command=view_records).pack(pady=5)

    root.mainloop()