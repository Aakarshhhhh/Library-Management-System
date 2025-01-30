import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pymysql

# Database Connection
def db_connect():
    try:
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='THEmaster@2004',  # Your MySQL password
                                     database='libmgt',  # Your database name
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Connection Error", str(e))
        return None

# Custom Dialog for Data Entry
class DataEntryDialog(tk.Toplevel):
    def __init__(self, parent, title, fields):
        super().__init__(parent)
        self.title(title)
        self.result = None

        # Frame for the form entries
        entry_frame = ttk.Frame(self)
        entry_frame.pack(padx=10, pady=10, fill='x', expand=True)

        self.entries = {}
        for field in fields:
            row = ttk.Frame(entry_frame)
            row.pack(side='top', fill='x', padx=5, pady=5)

            label = ttk.Label(row, text=f"{field}:", width=15)
            label.pack(side='left')

            entry = ttk.Entry(row)
            entry.pack(side='right', expand=True, fill='x')
            self.entries[field] = entry

        # Frame for the buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10)

        ttk.Button(button_frame, text="Submit", command=self.on_submit, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, style='Accent.TButton').pack(side='left', padx=5)

    def on_submit(self):
        self.result = {field: entry.get() for field, entry in self.entries.items()}
        self.destroy()

    def cancel(self):
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result

# CRUD Operations
def add_data(table, columns):
    dialog = DataEntryDialog(window, f"Add Data to {table}", columns)
    data = dialog.show()
    if data:
        conn = db_connect()
        if conn is None:
            return
        with conn.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(data))
            column_names = ', '.join(columns)
            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            try:
                cursor.execute(sql, list(data.values()))
                conn.commit()
                messagebox.showinfo("Success", f"Data added to {table} successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

def view_data(table, treeview, columns):
    conn = db_connect()
    if conn is None:
        return
    with conn.cursor() as cursor:
        sql = f"SELECT * FROM {table}"
        cursor.execute(sql)
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for row in records:
            treeview.insert('', tk.END, values=[row[col] for col in columns])
    conn.close()

def delete_data(table, id_column):
    record_id = simpledialog.askstring("Delete Record", f"Enter {id_column} to delete:")
    if record_id:
        conn = db_connect()
        if conn is None:
            return
        with conn.cursor() as cursor:
            sql = f"DELETE FROM {table} WHERE {id_column} = %s"
            try:
                cursor.execute(sql, (record_id,))
                conn.commit()
                if cursor.rowcount == 0:
                    messagebox.showinfo("Info", "No record found with the given ID.")
                else:
                    messagebox.showinfo("Success", "Record deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()
    else:
        messagebox.showinfo("Info", "Deletion cancelled, no ID provided.")

# Setup GUI with Tabs
def setup_ui(window):
    window.title("Library Management System")
    window.geometry('1400x700')
    window.configure(bg='#ff0000')

    style = ttk.Style(window)
    style.configure('Accent.TButton', background='#ff00ff', foreground='cyan')

    tab_control = ttk.Notebook(window)

    # Table details
    tables = {
        'Library': ['library_id', 'library_name', 'library_location'],
        'Member': ['member_id', 'member_type', 'member_address', 'member_contact_no', 'member_name_first', 'member_name_last'],
        'Staff': ['staff_id', 'staff_name_first', 'staff_name_last', 'staff_position', 'staff_salary'],
        'Student': ['student_id', 'student_name'],
        'Faculty_Staff': ['faculty_id', 'faculty_name'],
        'Author': ['author_id', 'author_name_first', 'author_name_last', 'author_nationality'],
        'Library_Card': ['card_id', 'expiry_date', 'card_status', 'member_id'],
        'Payment': ['payment_id', 'payment_date', 'member_id'],
        'Loan_History': ['loan_id', 'book_id', 'member_id', 'loan_date'],
        'Borrowing_Record': ['record_id', 'borrowed_date', 'return_date', 'book_id', 'member_id'],
        'Genre': ['genre_name', 'genre_type'],
        'Books': ['book_id', 'book_title', 'book_price', 'book_status'],
        'Overdue_Notice': ['notice_id', 'member_id', 'notice_status', 'notice_date', 'book_id'],
        'Admin': ['admin_id', 'admin_name_first', 'admin_name_last', 'admin_contact_no', 'admin_role'],
        'Fine': ['fine_id', 'fine_amount', 'member_id', 'fine_date'],
        'Supplier': ['supplier_id', 'supplier_name_first', 'supplier_name_last', 'supplier_location', 'supplier_contact_no'],
        'Publisher': ['publisher_id', 'publisher_name_first', 'publisher_name_last', 'publisher_location']
    }

    for table, cols in tables.items():
        tab = ttk.Frame(tab_control)
        tab_control.add(tab, text=table)

        # Treeview for displaying data
        tree = ttk.Treeview(tab, columns=cols, show='headings', style='Custom.Treeview')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=100)
        tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Buttons for CRUD operations
        ttk.Button(tab, text="View Data", command=lambda t=table, tr=tree, c=cols: view_data(t, tr, c), style='Accent.TButton').pack(pady=10, padx=10, side='left')
        ttk.Button(tab, text="Add Data", command=lambda t=table, c=cols: add_data(t, c), style='Accent.TButton').pack(pady=10, padx=10, side='left')
        ttk.Button(tab, text="Delete Data", command=lambda t=table, id_col=cols[0]: delete_data(t, id_col), style='Accent.TButton').pack(pady=10, padx=10, side='left')

    tab_control.pack(expand=1, fill='both')

# Main function
def main():
    global window
    window = tk.Tk()
    setup_ui(window)
    window.mainloop()

if __name__ == "__main__":
    main()
